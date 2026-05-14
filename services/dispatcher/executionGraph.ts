export type ExecutionNodeType =
  | "packet"
  | "approval"
  | "validation"
  | "worker"
  | "policy"
  | "telemetry";

export interface ExecutionNode {
  nodeId: string;
  type: ExecutionNodeType;
  label: string;
  status: "pending" | "ready" | "running" | "blocked" | "complete";
  dependsOn: string[];
  assignedWorkerId?: string;
  packetId?: string;
}

export interface ExecutionGraph {
  graphId: string;
  nodes: ExecutionNode[];
  createdAt: string;
}

export interface ExecutionPlan {
  graphId: string;
  readyNodes: ExecutionNode[];
  blockedNodes: ExecutionNode[];
  completeNodes: ExecutionNode[];
  generatedAt: string;
}

function completedNodeIds(nodes: ExecutionNode[]): Set<string> {
  return new Set(
    nodes.filter((node) => node.status === "complete").map((node) => node.nodeId)
  );
}

function dependenciesSatisfied(
  node: ExecutionNode,
  completed: Set<string>
): boolean {
  return node.dependsOn.every((dependencyId) => completed.has(dependencyId));
}

export function generateExecutionPlan(graph: ExecutionGraph): ExecutionPlan {
  const completed = completedNodeIds(graph.nodes);
  const readyNodes: ExecutionNode[] = [];
  const blockedNodes: ExecutionNode[] = [];
  const completeNodes = graph.nodes.filter((node) => node.status === "complete");

  for (const node of graph.nodes) {
    if (node.status === "complete") {
      continue;
    }

    if (node.status === "blocked") {
      blockedNodes.push(node);
      continue;
    }

    if (dependenciesSatisfied(node, completed)) {
      readyNodes.push({ ...node, status: "ready" });
    } else {
      blockedNodes.push({ ...node, status: "blocked" });
    }
  }

  return {
    graphId: graph.graphId,
    readyNodes,
    blockedNodes,
    completeNodes,
    generatedAt: new Date().toISOString()
  };
}

export function createPacketExecutionGraph(
  graphId: string,
  packetId: string
): ExecutionGraph {
  return {
    graphId,
    createdAt: new Date().toISOString(),
    nodes: [
      {
        nodeId: `${packetId}:policy`,
        type: "policy",
        label: "Evaluate policy",
        status: "pending",
        dependsOn: [],
        packetId
      },
      {
        nodeId: `${packetId}:approval`,
        type: "approval",
        label: "Confirm approval",
        status: "pending",
        dependsOn: [`${packetId}:policy`],
        packetId
      },
      {
        nodeId: `${packetId}:validation`,
        type: "validation",
        label: "Run clean-state validation",
        status: "pending",
        dependsOn: [`${packetId}:approval`],
        packetId
      },
      {
        nodeId: `${packetId}:worker`,
        type: "worker",
        label: "Assign worker",
        status: "pending",
        dependsOn: [`${packetId}:validation`],
        packetId
      },
      {
        nodeId: `${packetId}:telemetry`,
        type: "telemetry",
        label: "Write telemetry",
        status: "pending",
        dependsOn: [`${packetId}:worker`],
        packetId
      }
    ]
  };
}
