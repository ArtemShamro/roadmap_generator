import axios from "axios";

console.log("VITE_SIM_API_URL:", import.meta.env.VITE_SIM_API_URL);
console.log("VITE_AGENT_API_URL:", import.meta.env.VITE_AGENT_API_URL);

export const apiAgent = axios.create({
  baseURL: import.meta.env.VITE_AGENT_API_URL || "/api/agent",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

export const apiSim = axios.create({
  baseURL: import.meta.env.VITE_SIM_API_URL || "/api/sim",
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});
