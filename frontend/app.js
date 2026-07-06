const { createApp } = Vue

createApp({

    data() {

        return {

            currentPage: "home",

            // Authentication
            name: "",
            email: "",
            password: "",
            message: "",
            userRole: "",

            // Admin Dashboard
            adminPage: "dashboard",

            // Trek Details
            trekName: "",
            location: "",
            difficulty: "",
            duration: "",
            availableSlots: "",

            // Dashboard Stats
            totalTreks: 0,

            // Trek List
            treks: []

        }

    },

    methods: {

        goTo(page) {

            this.currentPage = page
            this.message = ""

        },

        goToAdmin(page) {

            this.adminPage = page
            this.message = ""

            if (page === "dashboard") {
                this.loadDashboard()
            }

            if (page === "manage-treks") {
                this.loadTreks()
            }

        },

        async loadDashboard() {

            try {

                const response = await fetch("http://127.0.0.1:5000/treks")

                const data = await response.json()

                this.totalTreks = data.length

            }

            catch (error) {

                console.log(error)

            }

        },

        async loadTreks() {

            try {

                const response = await fetch("http://127.0.0.1:5000/treks")

                const data = await response.json()

                this.treks = data

            }

            catch (error) {

                console.log(error)

            }

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
                    credentials: "include",

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

            }

            catch (error) {

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
                    credentials: "include",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        email: this.email,
                        password: this.password

                    })

                })

                const data = await response.json()

                this.message = data.message

                if (data.message === "Login successful") {

                    this.userRole = data.role

                    if (data.role === "user") {

                        this.currentPage = "user-dashboard"

                    }

                    else if (data.role === "admin") {

                        this.currentPage = "admin-dashboard"
                        this.adminPage = "dashboard"

                        this.loadDashboard()

                    }

                    else if (data.role === "staff") {

                        this.currentPage = "staff-dashboard"

                    }

                }

            }

            catch (error) {

                this.message = "Connection error"

            }

        },

                async addTrek() {

            if (

                this.trekName.trim() === "" ||
                this.location.trim() === "" ||
                this.difficulty.trim() === "" ||
                this.duration === "" ||
                this.availableSlots === ""

            ) {

                this.message = "Please fill all fields"
                return

            }

            try {

                const response = await fetch("http://127.0.0.1:5000/add_trek", {

                    method: "POST",
                    credentials: "include",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        trek_name: this.trekName,
                        location: this.location,
                        difficulty: this.difficulty,
                        duration: this.duration,
                        available_slots: this.availableSlots

                    })

                })

                const data = await response.json()

                this.message = data.message

                if (response.ok) {

                    this.trekName = ""
                    this.location = ""
                    this.difficulty = ""
                    this.duration = ""
                    this.availableSlots = ""

                    this.loadDashboard()
                    this.loadTreks()

                }

            }

            catch (error) {

                this.message = "Connection error"

            }

        },

        async deleteTrek(id) {

            const confirmDelete = confirm("Are you sure you want to delete this trek?")

            if (!confirmDelete) {
                return
            }

            try {

                const response = await fetch(
                    `http://127.0.0.1:5000/delete_trek/${id}`,
                    {
                        method: "DELETE",
                        credentials: "include"
                    }
                )

                const data = await response.json()

                this.message = data.message

                if (response.ok) {

                    this.loadTreks()
                    this.loadDashboard()

                }

            }

            catch (error) {

                this.message = "Connection error"

            }

        }

    }

}).mount("#app")