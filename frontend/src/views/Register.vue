<template>
  hi
  <DynamicFormModal
    :show="true"
    title="Register"
    :schema="registerSchema"
    :fetchUrl="null" 
    :submitUrl="submitUrl"
    method="POST"
    modalSize="modal-lg"
    @saved="onSuccess"
  />
</template>

<script setup>
import DynamicFormModal from "@/components/DynamicFormModal.vue";
import { registerSchema } from "@/schemas/registerSchema";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";

const router = useRouter();
const toast = useToast();

const submitUrl = "/api/auth/register";

function onSuccess() {
  toast.success("Registration successful!");
  router.push("/login");
}
</script>
