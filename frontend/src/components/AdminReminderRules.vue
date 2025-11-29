<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-bold">Reminder Rules</h2>
      <button class="btn btn-primary" @click="loadRules">Refresh</button>
    </div>

    <!-- Card: Create Rule -->
    <div class="card shadow-sm mb-4">
      <div class="card-header bg-dark text-white">
        <h5 class="mb-0">Create / Edit Reminder Rule</h5>
      </div>

      <div class="card-body">

        <!-- Rule Type -->
        <div class="mb-3">
          <label class="form-label fw-semibold">Rule Type</label>
          <select class="form-select" v-model="form.type">
            <option disabled value="">-- Select Rule Type --</option>
            <option value="not_visited_hours">User not visited for X hours</option>
            <option value="stay_exceeds_hours">Stay exceeds certain hours</option>
            <option value="new_facility_available">New facility to visit</option>
          </select>
        </div>

        <!-- Parameter Input -->
        <div class="mb-3" v-if="form.type === 'not_visited_hours'">
          <label class="form-label fw-semibold">Hours of inactivity</label>
          <input type="number" class="form-control" v-model="form.hours" />
        </div>

        <div class="mb-3" v-if="form.type === 'stay_exceeds_hours'">
          <label class="form-label fw-semibold">Stay exceeds (hours)</label>
          <input type="number" class="form-control" v-model="form.hours" />
        </div>

        <!-- Message -->
        <div class="mb-3">
          <label class="form-label fw-semibold">Message to Send</label>
          <textarea class="form-control" rows="3" v-model="form.message"
            placeholder="Enter the message the user will receive."></textarea>
        </div>

        <!-- Time Picker -->
        <div class="mb-3">
          <label class="form-label fw-semibold">Send Time (User’s chosen time)</label>
          <input type="time" class="form-control" v-model="form.schedule_time" />
        </div>

        <!-- Save Button -->
        <button class="btn btn-success" @click="saveRule">
          Save Rule
        </button>
      </div>
    </div>

    <!-- List of Rules -->
    <div class="card shadow-sm">
      <div class="card-header bg-secondary text-white">
        <h5 class="mb-0">Existing Rules</h5>
      </div>

      <div class="card-body">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>Rule Type</th>
              <th>Message</th>
              <th>Daily Time</th>
              <th>Parameters</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="rule in rules" :key="rule.id">
              <td>{{ prettyRule(rule.type) }}</td>
              <td>{{ rule.message }}</td>
              <td>{{ rule.schedule_time }}</td>
              <td>
                <span v-if="rule.hours">Hours: {{ rule.hours }}</span>
              </td>
              <td>
                <button class="btn btn-sm btn-outline-primary"
                        @click="runNow(rule.id)">
                  Run Now
                </button>
              </td>
            </tr>
          </tbody>
        </table>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import apiClient from "@/api/apiClient";

const rules = ref([]);

const form = ref({
  type: "",
  hours: null,
  message: "",
  schedule_time: "18:00"
});

const loadRules = async () => {
  try {
        const res = await apiClient.get("/admin/rules/reminder");
        const payload = res?.data ?? res;

        rules.value = payload.rules ?? [];
        console.log("Loaded rules:", rules.value);
    } catch (err) {
        console.error("Error loading rules", err);
    }
};

const saveRule = async () => {
  try {
    await apiClient.post("/admin/rules/reminder", form.value);
    await loadRules();
    alert("Rule saved successfully!");
  } catch (err) {
    console.error("Error saving rule", err);
    alert("Failed to save rule.");
  }
};

const runNow = async (ruleId) => {
  try {
    await apiClient.post(`/admin/rules/${ruleId}/run`);
    alert("Rule executed. Check reminder DB.");
  } catch (err) {
    console.error("Error running rule", err);
  }
};

const prettyRule = (code) => {
  switch (code) {
    case "not_visited_hours": return "User inactive for hours";
    case "stay_exceeds_hours": return "Stay exceeds hours";
    case "new_facility_available": return "New facility announcement";
    default: return code;
  }
};

onMounted(loadRules);
</script>

<style scoped>
.card {
  border-radius: 12px;
}
thead {
  background: #f8f9fa;
}
</style>
