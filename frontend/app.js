const { createApp } = Vue

createApp({
    data() {
        return {
            currentPage: "home",
            name: "",
            email: "",
            password: "",
            message: "",
            userRole: ""
        }
    },

    methods: {
        goTo(page) {
            this.currentPage = page
            this.message = ""
        },

        async registerUser() {

            if (
                this.name.trim() === "" ||
                this.email.trim() === "" ||
                this.password.trim() === ""
            ) {
                this.message = "Please fill all fields"
                return
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: this.name,
                        email: this.email,
                        password: this.password
                    })
                })

                const data = await response.json()
                this.message = data.message
            } catch (error) {
                this.message = "Connection error"
            }
        },

        async loginUser() {

            if (
                this.email.trim() === "" ||
                this.password.trim() === ""
            ) {
                this.message = "Please enter email and password"
                return
            }

            try {
                const response = await fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: this.email,
                        password: this.password
                    })
                })

                const data = await response.json()
                console.log(data)
                this.message = data.message

                if (data.message === "Login successful") {
                    this.userRole = data.role

                    if (data.role === "user") {
                        this.currentPage = "user-dashboard"
                    }
                    else if (data.role === "admin") {
                        this.currentPage = "admin-dashboard"
                    }
                    else if (data.role === "staff") {
                        this.currentPage = "staff-dashboard"
                    }
                }

            } catch (error) {
                this.message = "Connection error"
            }
        }
    }
}).mount("#app")