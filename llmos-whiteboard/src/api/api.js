import {API_BASE_URL} from "../config/api";

export const event_call = async (args, kwargs) => {
    try {
      const data = { "args":args,"kwargs": kwargs };
      const res = await fetch(`${API_BASE_URL}/windows/event_call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return res;
    } catch (error) {
      console.error("Failed to update data on the server:", error);
      throw error;
    }
  };


export async function callLLM(fullPrompt) {
  try {
    const res = await fetch(`${API_BASE_URL}/llm/call`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: fullPrompt }),
    });

    const data = await res.json();
    return { ok: true, data };
  } catch (err) {
    console.error("LLM 调用失败:", err);
    return { ok: false, error: "调用失败，请检查后端。" };
  }
}

export async function sendManualResponse(manualResponse) {
  try {
    const res = await fetch(`${API_BASE_URL}/llm/manual-response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ response: manualResponse }),
    });

    if (!res.ok) {
      return { ok: false, error: "发送失败，请检查后端连接" };
    }

    // 注意：res.json 也要 await
    const parsedCalls = await res.json();

    return {
      ok: true,
      parsedCalls,
    };
  } catch (err) {
    console.error("Manual response error:", err);
    return {
      ok: false,
      error: "发送失败，请检查网络连接",
    };
  }
}