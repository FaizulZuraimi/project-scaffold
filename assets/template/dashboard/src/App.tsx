import { useEffect, useState } from "react";

export function App() {
  const [status, setStatus] = useState("checking");

  useEffect(() => {
    void fetch("/api/health")
      .then((response) => (response.ok ? "up" : "down"))
      .catch(() => "down")
      .then(setStatus);
  }, []);

  return (
    <main>
      <h1>{{PROJECT_NAME}}</h1>
      <p>Backend: {status}</p>
    </main>
  );
}
