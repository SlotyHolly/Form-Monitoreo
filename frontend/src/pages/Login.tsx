import React, { useState } from "react";
import {
  Container,
  TextField,
  Button,
  Typography,
  Card,
  CardContent,
} from "@mui/material";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const Login = () => {
  const [credentials, setCredentials] = useState({ username: "", password: "" });
  const [error] = useState("");
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({ ...credentials, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
        const response = await axios.post(
            "http://127.0.0.1:5000/api/login",
            {
                username: credentials.username,
                password: credentials.password,
            },
            {
                headers: { 
                    "Content-Type": "application/json"
                },
                withCredentials: true,  // ✅ Esto permite que las cookies sean enviadas
            }
        );

        console.log("✅ Usuario autenticado:", response.data);
        navigate("/create_report");
    } catch (error) {
        console.error("❌ Error en login:", (error as any).response?.data);
    }
};

  return (
    <Container maxWidth="xs">
      <Card sx={{ mt: 10, p: 3 }}>
        <CardContent>
          <Typography variant="h5" component="h1" gutterBottom>
            Iniciar Sesión
          </Typography>

          {error && (
            <Typography color="error" sx={{ mb: 2 }}>
              {error}
            </Typography>
          )}

          <form onSubmit={handleLogin}>
            <TextField
              fullWidth
              label="Usuario"
              name="username"
              variant="outlined"
              margin="normal"
              value={credentials.username}
              onChange={handleChange}
              required
            />
            <TextField
              fullWidth
              label="Contraseña"
              name="password"
              type="password"
              variant="outlined"
              margin="normal"
              value={credentials.password}
              onChange={handleChange}
              required
            />
            <Button fullWidth variant="contained" color="primary" type="submit" sx={{ mt: 2 }}>
              Ingresar
            </Button>
          </form>
        </CardContent>
      </Card>
    </Container>
  );
};

export default Login;
