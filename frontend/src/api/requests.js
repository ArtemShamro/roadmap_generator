import { apiAgent, apiSim } from "./apxios";

export async function GenerateRoadmap({ command }) {
  console.log("api function GenerateRoadmap:", command);
  const data = { description: command };
  try {
    const response = await apiAgent.post("/generate", data);
    return response.data;
  } catch (error) {
    console.error(error);
    return null;
  }
}

export async function UpdateRoadmap({ roadmapId, command }) {
  console.log("api function UpdateRoadmap:", roadmapId, command);
  const data = { roadmap_id: roadmapId, command: command };
  try {
    const response = await apiAgent.put(`/update`, data);
    return response.data;
  } catch (error) {
    console.error(error);
    return null;
  }
}

export async function GetArticles({ query, k = 10 }) {
  console.log("api function GetArticles query:", query);
  const data = { query: query, k: k };
  try {
    const response = await apiSim.post("/search", data);
    console.log("api function GetArticles response:", response.data);
    return response.data;
  } catch (error) {
    console.error(error);
    return null;
  }
}
