import SwiftUI

struct LoginView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var authStore: AuthStore

    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @State private var isRegisterMode = false
    @State private var isSubmitting = false

    var body: some View {
        NavigationStack {
            Form {
                Section("Account") {
                    TextField("Username", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()

                    if isRegisterMode {
                        TextField("Email", text: $email)
                            .textInputAutocapitalization(.never)
                            .keyboardType(.emailAddress)
                            .autocorrectionDisabled()
                    }

                    SecureField("Password", text: $password)
                }

                if let errorMessage = authStore.errorMessage, !errorMessage.isEmpty {
                    Section {
                        Text(errorMessage)
                            .foregroundStyle(.red)
                    }
                }
            }
            .navigationTitle(isRegisterMode ? "Create Account" : "Sign In")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Close") { dismiss() }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button(isRegisterMode ? "Create" : "Sign In") {
                        Task {
                            await submit()
                        }
                    }
                    .disabled(username.isEmpty || password.isEmpty || isSubmitting)
                }
            }
            .safeAreaInset(edge: .bottom) {
                Button(isRegisterMode ? "Already have an account?" : "Need an account?") {
                    isRegisterMode.toggle()
                }
                .padding()
            }
        }
    }

    private func submit() async {
        isSubmitting = true
        defer { isSubmitting = false }

        let succeeded: Bool
        if isRegisterMode {
            succeeded = await authStore.register(username: username, email: email, password: password)
        } else {
            succeeded = await authStore.login(username: username, password: password)
        }

        if succeeded {
            dismiss()
        }
    }
}
