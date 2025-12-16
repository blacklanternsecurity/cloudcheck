use crate::CloudCheck as RustCloudCheck;
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[pymodule]
fn cloudcheck(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<CloudCheck>()?;
    Ok(())
}

#[pyclass(name = "CloudCheck")]
pub struct CloudCheck {
    inner: RustCloudCheck,
}

#[pymethods]
impl CloudCheck {
    #[new]
    fn new() -> Self {
        CloudCheck {
            inner: RustCloudCheck::new(),
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
                        result.push(dict.unbind().into());
                    }
                    Ok(result)
                }),
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                    "CloudCheck error: {}",
                    e
                ))),
            }
        })
    }

    fn regex_match<'py>(
        &self,
        py: Python<'py>,
        provider_name: &str,
        regex_name: &str,
        text: &str,
    ) -> PyResult<Bound<'py, PyAny>> {
        let inner = self.inner.clone();
        let provider_name = provider_name.to_string();
        let regex_name = regex_name.to_string();
        let text = text.to_string();
        pyo3_async_runtimes::tokio::future_into_py(py, async move {
            match inner.regex_match(&provider_name, &regex_name, &text).await {
                Ok(matched) => Ok(matched),
                Err(e) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                    "CloudCheck error: {}",
                    e
                ))),
            }
        })
    }
}
