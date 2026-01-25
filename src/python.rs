use crate::CloudCheck as RustCloudCheck;
use pyo3::create_exception;
use pyo3::prelude::*;
use pyo3::types::PyDict;

create_exception!(cloudcheck, CloudCheckError, pyo3::exceptions::PyException);

#[pymodule]
fn cloudcheck(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CloudCheck>()?;
    m.add("CloudCheckError", _py.get_type::<CloudCheckError>())?;
    Ok(())
}

#[pyclass(name = "CloudCheck")]
pub struct CloudCheck {
    inner: RustCloudCheck,
}

#[pymethods]
impl CloudCheck {
    #[new]
    #[pyo3(signature = (signature_url=None, max_retries=None, retry_delay_seconds=None, force_refresh=None))]
    fn new(
        signature_url: Option<String>,
        max_retries: Option<u32>,
        retry_delay_seconds: Option<u64>,
        force_refresh: Option<bool>,
    ) -> Self {
        CloudCheck {
            inner: RustCloudCheck::with_config(
                signature_url,
                max_retries,
                retry_delay_seconds,
                force_refresh,
            ),
        }
    }

    fn lookup<'py>(&self, py: Python<'py>, target: &str) -> PyResult<Bound<'py, PyAny>> {
        let inner = self.inner.clone();
        let target = target.to_string();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            match inner.lookup(&target).await {
                Ok(providers) => Python::attach(|py| -> PyResult<Vec<Py<PyAny>>> {
                    let mut result = Vec::new();
                    for provider in providers {
                        let dict = PyDict::new(py);
                        dict.set_item("name", provider.name)?;
                        dict.set_item("tags", provider.tags)?;
                        dict.set_item("short_description", provider.short_description)?;
                        dict.set_item("long_description", provider.long_description)?;
                        result.push(dict.unbind().into());
                    }
                    Ok(result)
                }),
                Err(e) => Err(PyErr::new::<CloudCheckError, _>(format!("{}", e))),
            }
        })
    }
}
