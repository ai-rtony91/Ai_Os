export interface CleanStateInput {
  branchStatus: string;
  changedFiles: string[];
  allowedFiles: string[];
  blockedFiles: string[];
}

export interface CleanStateResult {
  clean: boolean;
  blocked: boolean;
  reason: string;
  changedFiles: string[];
}

function matchesPattern(file: string, pattern: string): boolean {
  const escaped = pattern
    .replace(/[.+^${}()|[\]\\]/g, "\\$&")
    .replace(/\*/g, ".*");

  return new RegExp(`^${escaped}$`).test(file);
}

export function verifyCleanState(input: CleanStateInput): CleanStateResult {
  if (input.changedFiles.length === 0) {
    return {
      clean: true,
      blocked: false,
      reason: "Working tree is clean",
      changedFiles: []
    };
  }

  const blockedFile = input.changedFiles.find((file) =>
    input.blockedFiles.some((pattern) => matchesPattern(file, pattern))
  );

  if (blockedFile) {
    return {
      clean: false,
      blocked: true,
      reason: `Blocked file changed: ${blockedFile}`,
      changedFiles: input.changedFiles
    };
  }

  const outOfScopeFile = input.changedFiles.find(
    (file) => !input.allowedFiles.some((pattern) => matchesPattern(file, pattern))
  );

  if (outOfScopeFile) {
    return {
      clean: false,
      blocked: true,
      reason: `Changed file is outside packet scope: ${outOfScopeFile}`,
      changedFiles: input.changedFiles
    };
  }

  return {
    clean: false,
    blocked: false,
    reason: "Working tree has allowed packet-scoped changes",
    changedFiles: input.changedFiles
  };
}
