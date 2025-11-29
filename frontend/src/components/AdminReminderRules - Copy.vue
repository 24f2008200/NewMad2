

<template>
  <div class="container mt-4">

    <h2>Reminder Rule Editor</h2>

    <div class="card p-3 mb-4">
      <label>Trigger Type:</label>
      <select v-model="form.trigger_type" class="form-control">
        <option disabled value="">Select rule</option>
        <option value="stay_exceeding_hours">Stay exceeding certain hours</option>
        <option value="not_seen_for_hours">Not seen for some hours</option>
        <option value="new_parking_lot_created">New facility to visit</option>
      </select>

      <label class="mt-3">Message Template:</label>
      <textarea v-model="form.message_template" class="form-control"></textarea>

      <label class="mt-3">Daily Time:</label>
      <input type="time" v-model="form.time_of_day" class="form-control" />

      <button class="btn btn-primary mt-3" @click="saveRule">Save Rule</button>
    </div>

    <h3>Existing Rules</h3>
    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th><th>Trigger</th><th>Message</th><th>Schedule</th><th>Active</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="rule in rules" :key="rule.id">
          <td>{{ rule.id }}</td>
          <td>{{ rule.trigger_type }}</td>
          <td>{{ rule.message_template }}</td>
          <td>{{ rule.time_of_day }}</td>
          <td>{{ rule.active }}</td>
        </tr>
      </tbody>
    </table>

  </div>
</template>
<script setup>
import { ref, onMounted } from "vue";
import apiClient from "@/apiClient";

const rules = ref([]);
const form = ref({
  trigger_type: "",
  message_template: "",
  schedule_type: "daily",
  time_of_day: "18:00",
  active: true,
});

async function loadRules() {
  
  try {
        const res = await apiClient.get("/admin/rules/reminder");
        const payload = res?.data ?? res;

        rules.value = payload.rules ?? [];
        console.log("Loaded rules:", rules.value);
    } catch (err) {
        console.error("Error loading rules", err);
    }
}

async function saveRule() {
  await apiClient.post("/admin/rules/reminder", form.value);
  await loadRules();
}

onMounted(loadRules);
</script>