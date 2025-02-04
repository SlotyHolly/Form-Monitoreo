import { useEffect, useState } from "react";
import axios from "axios";
import { Navigate } from "react-router-dom";

interface User {
    username: string;
    role: string;
}

const Dashboard = () => {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get("http://127.0.0.1:5000/api/check_session", { withCredentials: true })
            .then(response => {
                if (response.data.logged_in) {
                    setUser(response.data);
                }
            })
            .catch(() => setUser(null))
            .finally(() => setLoading(false));
    }, []);

    if (loading) return <p>Cargando...</p>;

    const handleLogout = () => {
        axios.post("http://127.0.0.1:5000/api/logout", {}, { withCredentials: true })
            .then(() => window.location.href = "/")
            .catch(err => console.error("Error al cerrar sesión:", err));
    };
    
    
    return user ? (
        <div>
            <h1>Bienvenido, {user.username}!</h1>
            <p>Tu rol es: {user.role}</p>
            <button onClick={handleLogout}>Cerrar sesión</button>
        </div>
    ) : (
        <Navigate to="/" />
    );
};

export default Dashboard;
