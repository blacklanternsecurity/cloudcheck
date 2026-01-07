import unittest
import subprocess
import requests
import time
import sys


class TestDocker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Build and start the Docker container."""
        print("Building Docker image...", file=sys.stderr)
        build_result = subprocess.run(
            ["docker", "build", "-t", "cloudcheck:test", "."],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if build_result.returncode != 0:
            print(f"Build failed: {build_result.stderr}", file=sys.stderr)
            raise Exception(f"Docker build failed: {build_result.stderr}")
        print("Build successful", file=sys.stderr)

        # Clean up any existing container
        subprocess.run(["docker", "rm", "-f", "cloudcheck-test"], capture_output=True)

        print("Starting container...", file=sys.stderr)
        result = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-p",
                "8080:8080",
                "--name",
                "cloudcheck-test",
                "cloudcheck:test",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"Container start failed: {result.stderr}", file=sys.stderr)
            raise Exception(f"Failed to start container: {result.stderr}")
        cls.container_id = result.stdout.strip()
        print(f"Container started: {cls.container_id}", file=sys.stderr)

        # Show container logs
        logs = subprocess.run(
            ["docker", "logs", "cloudcheck-test"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if logs.stdout:
            print("Container logs:", file=sys.stderr)
            print(logs.stdout, file=sys.stderr)
        if logs.stderr:
            print("Container stderr:", file=sys.stderr)
            print(logs.stderr, file=sys.stderr)

        # Wait for server to be ready and cache to populate
        cls.base_url = "http://localhost:8080"
        print("Waiting for server to be ready...", file=sys.stderr)
        for i in range(5):
            try:
                print(
                    f"Attempt {i + 1}/60: Checking {cls.base_url}/lookup/8.8.8.8",
                    file=sys.stderr,
                )
                response = requests.get(f"{cls.base_url}/lookup/8.8.8.8", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    # Wait until we actually get providers (cache might be loading)
                    if isinstance(data, list) and len(data) > 0:
                        print("Server is ready with data!", file=sys.stderr)
                        break
                    print(f"Got response but no providers yet: {data}", file=sys.stderr)
                else:
                    print(f"Got status code {response.status_code}", file=sys.stderr)
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}", file=sys.stderr)
            time.sleep(2)
        else:
            # Check container logs
            logs = subprocess.run(
                ["docker", "logs", "cloudcheck-test"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            print("Container logs on failure:", file=sys.stderr)
            if logs.stdout:
                print(logs.stdout, file=sys.stderr)
            if logs.stderr:
                print(logs.stderr, file=sys.stderr)
            cls.tearDownClass()
            raise Exception(
                "Container failed to start or server not ready after 60 attempts"
            )

    @classmethod
    def tearDownClass(cls):
        """Stop and remove the container."""
        print("Cleaning up container...", file=sys.stderr)
        # Try to stop gracefully, but don't fail if it times out
        try:
            subprocess.run(
                ["docker", "stop", "cloudcheck-test"], capture_output=True, timeout=5
            )
        except subprocess.TimeoutExpired:
            # If stop times out, force kill it
            print("Stop timed out, forcing kill...", file=sys.stderr)
            subprocess.run(
                ["docker", "kill", "cloudcheck-test"], capture_output=True, timeout=5
            )

        # Force remove the container (works even if it's still running)
        subprocess.run(
            ["docker", "rm", "-f", "cloudcheck-test"], capture_output=True, timeout=5
        )

    def test_lookup_endpoint(self):
        """Test the /lookup/{target} endpoint."""
        print(f"Testing {self.base_url}/lookup/8.8.8.8", file=sys.stderr)
        response = requests.get(f"{self.base_url}/lookup/8.8.8.8", timeout=10)
        self.assertEqual(
            response.status_code, 200, f"Expected 200, got {response.status_code}"
        )

        data = response.json()
        self.assertIsInstance(data, list, "Response should be an array")
        self.assertGreater(
            len(data), 0, "Response should contain at least one provider"
        )

        names = [p["name"] for p in data]
        self.assertIn("Google", names, f"Expected Google in providers: {names}")


if __name__ == "__main__":
    unittest.main()
