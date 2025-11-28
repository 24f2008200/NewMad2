import axios from "axios";

export default {

  async getAll() {
    const res = await axios.get("/api/tasks");
    return res.data;
  },

  async cancelTask(taskId) {
    const res = await axios.post(`/api/tasks/${taskId}/cancel`);
    return res.data;
  },

  async runTask(taskName, args = [], kwargs = {}) {
    const res = await axios.post("/api/tasks/run", {
      task: taskName,
      args,
      kwargs,
    });
    return res.data;
  },

};
