import { BrowserRouter, Routes, Route } from "react-router-dom";
import CreateReport from "./pages/CreateReport";
import Login from "./pages/Login";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/create_report" element={<CreateReport />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
