import { RUNTIME_VISIBILITY_SOURCE_LABELS } from "./runtimeVisibilityAdapter";

const RUNTIME_VISIBILITY_API_SCHEMA = "aios.runtime_visibility_api.v1";
const READ_ONLY_MODE = "READ_ONLY";

export const RUNTIME_VISIBILITY_CLIENT_ERROR_CODES = Object.freeze({
  API_UNAVAILABLE: "API_UNAVAILABLE",
  HTTP_ERROR: "HTTP_ERROR",
  INVALID_SCHEMA: "INVALID_SCHEMA",
  NON_READ_ONLY_RESPONSE: "NON_READ_ONLY_RESPONSE",
  UNKNOWN: "UNKNOWN"
});

export const DEFAULT_RUNTIME_VISIBILITY_CONFIG = Object.freeze({
  sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.MOCK_DATA,
  apiUrl: "/api/runtime/visibility",
  timeoutMs: 3000
});

export function getRuntimeVisibilityClientConfig(env = import.meta.env) {
  return {
    sourceLabel:
      env?.VITE_AIOS_RUNTIME_VISIBILITY_SOURCE ??
      DEFAULT_RUNTIME_VISIBILITY_CONFIG.sourceLabel,
    apiUrl:
      env?.VITE_AIOS_RUNTIME_VISIBILITY_URL ??
      DEFAULT_RUNTIME_VISIBILITY_CONFIG.apiUrl,
    timeoutMs: Number(
      env?.VITE_AIOS_RUNTIME_VISIBILITY_TIMEOUT_MS ??
        DEFAULT_RUNTIME_VISIBILITY_CONFIG.timeoutMs
    )
  };
}

export function createRuntimeVisibilityErrorState(error) {
  return {
    sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.UNKNOWN,
    loading: false,
    data: null,
    error: {
      code: error?.code ?? RUNTIME_VISIBILITY_CLIENT_ERROR_CODES.UNKNOWN,
      message: error?.message ?? "Runtime visibility source is unavailable."
    }
  };
}

export function validateRuntimeVisibilityApiSchema(data) {
  if (data?.schema !== RUNTIME_VISIBILITY_API_SCHEMA) {
    return {
      ok: false,
      code: RUNTIME_VISIBILITY_CLIENT_ERROR_CODES.INVALID_SCHEMA,
      message: "Runtime visibility API returned an unexpected schema."
    };
  }

  if (data?.mode !== READ_ONLY_MODE) {
    return {
      ok: false,
      code: RUNTIME_VISIBILITY_CLIENT_ERROR_CODES.NON_READ_ONLY_RESPONSE,
      message: "Runtime visibility API response was not read-only."
    };
  }

  return { ok: true, code: null, message: null };
}

export async function fetchRuntimeVisibilityReadOnly(config = getRuntimeVisibilityClientConfig()) {
  const response = await fetch(config.apiUrl, { method: "GET" });

  if (!response.ok) {
    throw {
      code: RUNTIME_VISIBILITY_CLIENT_ERROR_CODES.HTTP_ERROR,
      message: `Runtime visibility API returned HTTP ${response.status}.`
    };
  }

  const data = await response.json();
  const validation = validateRuntimeVisibilityApiSchema(data);

  if (!validation.ok) {
    throw validation;
  }

  return {
    sourceLabel: RUNTIME_VISIBILITY_SOURCE_LABELS.LOCAL_API_READ_ONLY,
    loading: false,
    data,
    error: null
  };
}
