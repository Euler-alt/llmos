import { useEffect, useState } from "react";
import { validateBackendConfig } from "../components/PromptWindows/ComponentRegistry";

const API_BASE_URL = 'http://localhost:3001/api';

export function useSseWindows() {
  const [windows, setWindows] = useState({});
  const [windowConfigs, setWindowConfigs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    const eventSource = new EventSource(`${API_BASE_URL}/sse`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 新格式
        if (data.windows && validateBackendConfig(data)) {
          setWindowConfigs(data.windows);

          const moduleData = { ...data };
          delete moduleData.windows;
          setWindows(moduleData);
        }
        // 旧格式
        else {
          setWindows(data);
          setWindowConfigs((prev) => {
            if (prev.length === 0) {
              return Object.keys(data).map((type, index) => ({
                id: `${type}-${index}`,
                type,
                title: type.charAt(0).toUpperCase() + type.slice(1),
                order: index
              }));
            }
            return prev;
          });
        }

        setLoading(false);
      } catch (err) {
        console.error("Failed to parse SSE data:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      eventSource.close();
      setLoading(false);
    };

    return () => {
      eventSource.close();
      console.log("SSE connection closed");
    };
  }, []);

  return { windows, windowConfigs, loading, setWindows, setWindowConfigs };
}
