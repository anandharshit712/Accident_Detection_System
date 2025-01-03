import React, { useState, useEffect } from "react";
import axios from "axios";
import Bedsupdate from "./Bedsupdate"
import AlertPage from "./alertpage";


function App() {
    
    return (<>
            <Bedsupdate/>
            <AlertPage/>
            </>
    );
}

export default App;
