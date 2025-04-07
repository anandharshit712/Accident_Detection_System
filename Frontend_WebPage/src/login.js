import React, { useState } from "react";
import {Link, useNavigate } from "react-router-dom";
import "./loginform.css";


const UserLoginForm = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        h_ID: "",
        password: ""
    });
    // Handle input changes
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    // Handle form submission using fetch API
    const handleSubmit = async (e) => {
        e.preventDefault();
        

        try {
            
            //const response = await fetch("https://admin-system-1.onrender.com/loginuser", {
                const response = await fetch("https://crash-api-six.vercel.app/hosp-login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            const result =await response.json();
            console.log(result);
            const {success}=result;

            if (success) {
                localStorage.setItem('Hospital_ID',formData.h_ID);
                alert("Log in successful")
                setTimeout(()=>{navigate("/userpage")},1000);
            } 
            else{alert("enter correct details")}
        } catch (error) {
            console.error("Error submitting form data:");
            alert("There was an error submitting the form.");
        }
    };
    

    return (
        <>
            
            <div className="form-container">
                <h2>Login</h2>

                <form onSubmit={handleSubmit}>

                    <label htmlFor="email_id">Email ID:</label>
                    <input
                        type="number"
                        id="h_ID"
                        name="h_ID"
                        placeholder="Enter ID"
                        value={formData.h_ID}
                        onChange={handleChange}
                        required
                    />
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        placeholder="Enter Password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                    <button className="lbutton" type="submit">Login</button>
                </form>
            </div>
        </>
    );
};

export default UserLoginForm;
