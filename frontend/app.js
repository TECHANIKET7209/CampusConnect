
const API = "http://127.0.0.1:8000";

const message = document.getElementById("message");

function showMessage(text, success = true) {
    if (!message) return;
    message.textContent = text;
    message.style.color = success ? "green" : "red";
}


async function apiRequest(path, method = "GET", data = null) {
    const token = sessionStorage.getItem("access_token");

    const options = {
        method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    if (data !== null) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(API + path, options);

    let result;
    try {
        result = await response.json();
    } catch {
        result = {};
    }

    if (!response.ok) {
        if (response.status === 401) {
            sessionStorage.clear();
            window.location.href = "login.html";
        }
        throw new Error(result.detail || "Something went wrong");
    }

    return result;
}


// Load Students
async function loadStudents() {
    try {
        const students = await apiRequest("/students/");

        document.getElementById("totalStudents").textContent =
            students.length;

        const table = document.getElementById("studentTable");
        table.innerHTML = "";

        students.forEach(student => {
            table.innerHTML += `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.roll_number}</td>
                    <td>${student.full_name}</td>
                    <td>${student.department}</td>
                    <td>${student.semester}</td>
                    <td>
                        <button class="btn btn-sm btn-warning"
                            onclick="editStudent(${student.id})">
                            Edit
                        </button>

                        <button class="btn btn-sm btn-danger"
                            onclick="deleteStudent(${student.id})">
                            Delete
                        </button>
                    </td>
                </tr>
            `;
        });

    } catch (error) {
        showMessage(error.message, false);
    }
}


// Edit Student
async function editStudent(id) {
    try {
        const students = await apiRequest("/students/");
        const student = students.find(s => s.id === id);

        if (!student) {
            showMessage("Student not found", false);
            return;
        }

        const roll = prompt("Enter Roll Number:", student.roll_number);
        if (roll === null) return;

        const name = prompt("Enter Full Name:", student.full_name);
        if (name === null) return;

        const email = prompt("Enter Email:", student.email);
        if (email === null) return;

        const department = prompt(
            "Enter Department:",
            student.department
        );
        if (department === null) return;

        const semester = prompt(
            "Enter Semester:",
            student.semester
        );
        if (semester === null) return;

        if (!roll.trim() || !name.trim() || !email.trim() ||
            !department.trim() || !semester.trim()) {
            showMessage("All fields are required", false);
            return;
        }

        const updatedStudent = {
            roll_number: roll.trim(),
            full_name: name.trim(),
            email: email.trim(),
            department: department.trim(),
            semester: Number(semester)
        };

        if (!Number.isInteger(updatedStudent.semester) ||
            updatedStudent.semester < 1) {
            showMessage("Enter a valid semester", false);
            return;
        }

        await apiRequest(`/students/${id}`, "PUT", updatedStudent);

        showMessage("Student updated successfully!");

        await refreshDashboard();

    } catch (error) {
        showMessage(error.message, false);
    }
}


// Delete Student
async function deleteStudent(id) {
    const confirmed = confirm(
        "Are you sure you want to delete this student? " +
        "Attendance and assessment records will also be deleted."
    );

    if (!confirmed) return;

    try {
        const result = await apiRequest(`/students/${id}`, "DELETE");

        showMessage(result.message || "Student deleted successfully!");

        document.getElementById("analyticsResult").innerHTML = "";

        await refreshDashboard();

    } catch (error) {
        showMessage(error.message, false);
    }
}


// Refresh Dashboard
async function refreshDashboard() {
    await loadStudents();
    await loadDashboardStats();
    await loadPerformanceCharts();
}


// Register Student
document.getElementById("studentForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        try {
            const student = await apiRequest("/students/", "POST", {
                roll_number: document.getElementById("roll").value.trim(),
                full_name: document.getElementById("name").value.trim(),
                email: document.getElementById("email").value.trim(),
                department: document.getElementById("department").value.trim(),
                semester: Number(
                    document.getElementById("semester").value
                )
            });

            showMessage(
                "Student registered successfully! ID: " + student.id
            );

            event.target.reset();

            await refreshDashboard();

        } catch (error) {
            showMessage(error.message, false);
        }
    }
);


// Mark Attendance
document.getElementById("attendanceDate").value =
    new Date().toLocaleDateString("en-CA");

document.getElementById("attendanceForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        try {
            const result = await apiRequest("/attendance/", "POST", {
                student_id: Number(
                    document.getElementById("attendanceStudentId").value
                ),
                status: document.getElementById("attendanceStatus").value,
                attendance_date:
                    document.getElementById("attendanceDate").value
            });

            showMessage(result.message);

            event.target.reset();

            document.getElementById("attendanceDate").value =
                new Date().toLocaleDateString("en-CA");

            await refreshDashboard();

        } catch (error) {
            showMessage(error.message, false);
        }
    }
);


// Save Assessment Marks
document.getElementById("marksForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        try {
            const result = await apiRequest("/assessments/", "POST", {
                student_id: Number(
                    document.getElementById("marksStudentId").value
                ),
                subject: document.getElementById("subject").value.trim(),
                marks_obtained: Number(
                    document.getElementById("marksObtained").value
                ),
                max_marks: Number(
                    document.getElementById("maxMarks").value
                )
            });

            showMessage(result.message);

            event.target.reset();
            document.getElementById("maxMarks").value = 100;

            await refreshDashboard();

        } catch (error) {
            showMessage(error.message, false);
        }
    }
);


// Academic Analytics
document.getElementById("analyticsForm").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        try {
            const id = document.getElementById(
                "analyticsStudentId"
            ).value;

            const result = await apiRequest(`/analytics/${id}`);

            const riskColor =
                result.risk_status === "At Risk"
                    ? "#dc3545"
                    : "#198754";

            document.getElementById("analyticsResult").innerHTML = `
                <div style="background:#f8fafc;padding:20px;border-radius:12px;">
                    <h4>${result.student_name}</h4>

                    <p>Attendance:
                        <strong>${result.attendance_percentage}%</strong>
                    </p>

                    <p>Average Marks:
                        <strong>${result.average_marks_percentage}%</strong>
                    </p>

                    <p>Assessments:
                        <strong>${result.assessments_count}</strong>
                    </p>

                    <h4 style="color:${riskColor}">
                        Risk Status: ${result.risk_status}
                    </h4>

                    <p>Reason:
                        ${result.risk_reasons.join(", ") || "No risk detected"}
                    </p>
                </div>
            `;

            await loadDashboardStats();
            await loadPerformanceCharts();

            showMessage("Academic analytics loaded successfully");

        } catch (error) {
            showMessage(error.message, false);
        }
    }
);


// Dashboard Statistics
async function loadDashboardStats() {
    try {
        const students = await apiRequest("/students/");

        let totalAttendance = 0;
        let atRiskCount = 0;
        let analyzedCount = 0;

        for (const student of students) {
            const result = await apiRequest(
                `/analytics/${student.id}`
            );

            if (result.risk_status !== "Insufficient Data") {
                analyzedCount++;
                totalAttendance += result.attendance_percentage;

                if (result.risk_status === "At Risk") {
                    atRiskCount++;
                }
            }
        }

        document.getElementById("atRisk").textContent = atRiskCount;

        document.getElementById("avgAttendance").textContent =
            analyzedCount
                ? (totalAttendance / analyzedCount).toFixed(1) + "%"
                : "0%";

    } catch (error) {
        showMessage(error.message, false);
    }
}


// Academic Performance Charts
let performanceChartInstance;
let riskChartInstance;
let attendanceChartInstance;

async function loadPerformanceCharts() {
    try {
        const students = await apiRequest("/students/");

        const analytics = await Promise.all(
            students.map(student =>
                apiRequest(`/analytics/${student.id}`)
            )
        );

        const names = analytics.map(s => s.student_name);
        const marks = analytics.map(s => s.average_marks_percentage);
        const attendance = analytics.map(s => s.attendance_percentage);

        const atRisk = analytics.filter(
            s => s.risk_status === "At Risk"
        ).length;

        const safe = analytics.length - atRisk;

        if (performanceChartInstance) {
            performanceChartInstance.destroy();
        }

        if (riskChartInstance) {
            riskChartInstance.destroy();
        }

        if (attendanceChartInstance) {
            attendanceChartInstance.destroy();
        }

        performanceChartInstance = new Chart(
            document.getElementById("performanceChart"),
            {
                type: "bar",
                data: {
                    labels: names,
                    datasets: [
                        {
                            label: "Marks (%)",
                            data: marks,
                            backgroundColor: "#0d6efd"
                        },
                        {
                            label: "Attendance (%)",
                            data: attendance,
                            backgroundColor: "#198754"
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            }
        );

        riskChartInstance = new Chart(
            document.getElementById("riskChart"),
            {
                type: "doughnut",
                data: {
                    labels: ["At Risk", "Safe"],
                    datasets: [{
                        data: [atRisk, safe],
                        backgroundColor: ["#dc3545", "#198754"]
                    }]
                },
                options: {
                    responsive: true
                }
            }
        );

        attendanceChartInstance = new Chart(
            document.getElementById("attendanceChart"),
            {
                type: "line",
                data: {
                    labels: names,
                    datasets: [{
                        label: "Attendance (%)",
                        data: attendance,
                        borderColor: "#6f42c1",
                        backgroundColor: "rgba(111,66,193,0.15)",
                        fill: true,
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            }
        );

    } catch (error) {
        showMessage("Charts error: " + error.message, false);
    }
}


// Initial Dashboard Load
refreshDashboard();

