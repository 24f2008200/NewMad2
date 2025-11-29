<template>
  <div class="container mt-4">

    <h2 class="mb-4">Reminder Rules Admin</h2>

    <!-- Add New Rule Button -->
    <button class="btn btn-primary mb-3" @click="openCreateModal">
      + Add New Rule
    </button>

    <!-- Rules Table -->
    <div class="card shadow-sm">
      <div class="card-body">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Status</th>
              <th>Trigger</th>
              <th>Message</th>
              <th>Schedule</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="rule in rules" :key="rule.id">
              <td>{{ rule.id }}</td>
              <td>{{ rule.rule_name }}</td>
              <td>{{ rule.active }}</td>
              <td>{{ rule.trigger_type }}</td>
              <td>{{ rule.message_template }}</td>

              <td>
                <span v-if="rule.schedule_type === 'daily'">
                  Daily @ {{ rule.time_of_day }}
                </span>
                <span v-else>
                  CRON: {{ rule.cron_expr }}
                </span>
              </td>

              <td>
                <span class="badge"
                      :class="rule.active ? 'bg-success' : 'bg-secondary'">
                  {{ rule.active ? "Active" : "Inactive" }}
                </span>
              </td>

              <td>
                <button class="btn btn-sm btn-warning me-2"
                        @click="openEditModal(rule)">
                  Edit
                </button>

                <button class="btn btn-sm btn-info me-2"
                        @click="runRuleNow(rule.id)">
                  ▶ Run Now
                </button>

                <button class="btn btn-sm btn-danger"
                        @click="deleteRule(rule.id)">
                  Delete
                </button>
              </td>
            </tr>
          </tbody>

        </table>
      </div>
    </div>

    <!-- MODAL -->
    <div class="modal fade" ref="modalRef" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">

          <div class="modal-header">
            <h5 class="modal-title">{{ isEdit ? "Edit Rule" : "New Rule" }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>

          <div class="modal-body">
            <form>
                <div class="mb-3">
                <label>Name</label>
                <input class="form-control" type="text" v-model="form.rule_name" >
                </div>

              <div class="mb-3">
                <label>Trigger Type</label>
                <select class="form-select" v-model="form.trigger_type">
                  <option disabled value="">Select trigger…</option>
                  <option value="stay_exceed_hours">Stay Exceeding 48 Hrs</option>
                  <option value="not_seen_days">Not Seen For 8 days</option>
                  <option value="new_facility">New Facility Created</option>
                  <option value="broadcast">Broadcast</option>
                </select>
              </div>
              <div class="mb-3">
                <label>Action</label>
                <select class="form-select" v-model="form.action">
                  <option disabled value="">Select action…</option>
                  <option value="send_reminder">Send Reminder</option>
                  <option value="mail_pdf">Mail PDF</option>
                  <option value="accounts_statement">Accounts Statement</option>
                </select>
              </div>


              <div class="mb-3">
                <label>Message Template</label>
                <textarea class="form-control" rows="2"
                          v-model="form.message_template"></textarea>
              </div>

              <div class="mb-3">
                <label>Schedule Type</label>
                <select class="form-select" v-model="form.schedule_type">
                  <option value="one_time">One Time</option>
                  <option value="hourly">Hourly</option>
                  <option value="daily">Daily</option>  
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <!-- Daily -->
              <div v-if="form.schedule_type === 'daily'" class="mb-3">
                <label>Time of Day</label>
                <input class="form-control" type="time" v-model="form.time_of_day">
              </div>

              <!-- Cron -->
              <div v-else class="mb-3">
                <label>Cron Expression</label>
                <input class="form-control" placeholder="0 18 * * *"
                       v-model="form.cron_expr">
              </div>

              <div class="form-check">
                <input class="form-check-input" type="checkbox"
                       v-model="form.active">
                <label class="form-check-label">Active</label>
              </div>

            </form>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button class="btn btn-primary" @click="saveRule">Save</button>
          </div>

        </div>
      </div>
    </div>

  </div>
</template>


<script setup>
import { ref, onMounted } from "vue";
import apiClient from "@/apiClient"; // your axios wrapper

const rules = ref([]);
const modalRef = ref(null);
let modalInstance = null;

const form = ref({
  id: null,
  trigger_type: "",
  message_template: "",
  schedule_type: "daily",
  time_of_day: "18:00",
  cron_expr: "",
  active: true,
});

const isEdit = ref(false);

onMounted(async () => {
  await loadRules();

  // Bootstrap modal
  const modalEl = modalRef.value;
  modalInstance = new bootstrap.Modal(modalEl);
});


// Load from backend
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


// Open modal for new rule
function openCreateModal() {
  isEdit.value = false;

  form.value = {
    id: null,
    trigger_type: "",
    message_template: "",
    schedule_type: "daily",
    time_of_day: "18:00",
    cron_expr: "",
    active: true,
  };

  modalInstance.show();
}


// Open modal for editing
function openEditModal(rule) {
  isEdit.value = true;
  form.value = { ...rule }; // clone
  modalInstance.show();
}


// Close modal
function closeModal() {
  modalInstance.hide();
}


// Save = create or update
async function saveRule() {
  try {
    if (isEdit.value) {
      await apiClient.put(`/admin/rules/reminder/${form.value.id}`, form.value);
    } else {
      await apiClient.post(`/admin/rules/reminder`, form.value);
    }

    modalInstance.hide();
    await loadRules();

  } catch (err) {
    console.error("Failed to save rule", err);
  }
}


// Delete
async function deleteRule(id) {
  if (!confirm("Delete this rule?")) return;
  await apiClient.del(`/admin/rules/reminder/${id}`);
  await loadRules();
}


// Run Now button
async function runRuleNow(id) {
  try {
    const res = await apiClient.post(`/admin/rules/reminder/${id}/run`);
    const payload = res?.data ?? res;
    
    alert(`Rule executed successfully! ${payload.jobs_created} reminder jobs created.`);
  } catch (err) {
    console.error("Failed to run rule", err);
    alert("Failed to execute rule.");
  }
}
</script>


<style scoped>
.table td {
  vertical-align: middle;
}
</style>
