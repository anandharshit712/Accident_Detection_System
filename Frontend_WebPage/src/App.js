import React from "react";
import { BrowserRouter as Router, Routes,Route, Navigate } from 'react-router-dom';
import UserLoginForm from "./login";
import SecondPage from "./SecondPage";


function App() {
    
    return (<>        
            <Router>
            <Routes>
              <Route exact path="/" element={<UserLoginForm/>} />      
              <Route exact path='/userpage' element={<SecondPage/>}/>
            </Routes>
            </Router>
            </>
    );
}

export default App;
