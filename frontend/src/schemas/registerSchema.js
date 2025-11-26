export const registerSchema = {
  sections: [
    {
      id: "core",
      label: "User Registration",
      fields: [
        { model: "name", label: "Name", type: "text", rules: ["required"] },
        { model: "email", label: "Email", type: "email", rules: ["required", "email"] },
        { model: "mobile", label: "Mobile", type: "text", rules: ["required"] },
        { model: "address", label: "Address", type: "textarea" },

        {
          model: "receive_reminders",
          label: "Receive Reminders",
          type: "select",
          options: [
            { label: "Yes", value: "Yes" },
            { label: "No", value: "No" }
          ]
        },

        { model: "reminder_time", label: "Reminder Time", type: "text" },
        { model: "google_chat_hook", label: "Google Chat Hook", type: "url" },

        // 🔥 Replace "password" with password-group
        {
          model: "password_group",
          label: "Password",
          type: "password-group",
          rules: ["passwordMatch"]
        }
      ]
    }
  ]
};
