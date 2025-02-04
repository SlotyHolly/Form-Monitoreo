import React, { useState } from "react";
import axios from "axios";
import { Container, Typography, Button, Box, Input, CircularProgress } from "@mui/material";

const CreateReport: React.FC = () => {
    const [files, setFiles] = useState<{ [key: string]: File | null }>({});
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const { name, files } = event.target;
        if (files && files.length > 0) {
            setFiles((prevFiles) => ({
                ...prevFiles,
                [name]: files[0],
            }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage("");
        setLoading(true);

        const formData = new FormData();
        Object.entries(files).forEach(([key, file]) => {
            if (file) {
                formData.append(key, file);
            }
        });

        try {
            const response = await axios.post("http://127.0.0.1:5000/api/upload_report", formData, {
                headers: { "Content-Type": "multipart/form-data" },
                withCredentials: true,  // 👈 Esto permite que Flask reconozca la sesión
            });

            setMessage(response.data.message);
        } catch (err) {
            setMessage("Error al subir los archivos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="sm">
            <Box sx={{ mt: 5, p: 3, boxShadow: 3, borderRadius: 2 }}>
                <Typography variant="h5" gutterBottom>
                    Subir Reportes CSV
                </Typography>

                <form onSubmit={handleSubmit}>
                    {[
                        { name: "failed_users", label: "Usuarios con Fallos de Conexión" },
                        { name: "failed_ips", label: "IPs con Fallos de Conexión" },
                        { name: "blocked_users", label: "Usuarios Bloqueados" },
                        { name: "blocked_ips", label: "IPs Bloqueadas" },
                        { name: "users_added", label: "Usuarios Agregados (Opcional)" },
                    ].map((input) => (
                        <Box key={input.name} sx={{ mb: 2 }}>
                            <Typography variant="body1">{input.label}</Typography>
                            <Input type="file" name={input.name} onChange={handleFileChange} />
                        </Box>
                    ))}

                    <Button type="submit" variant="contained" color="primary" disabled={loading}>
                        {loading ? <CircularProgress size={24} /> : "Subir Reportes"}
                    </Button>
                </form>

                {message && <Typography sx={{ mt: 2 }}>{message}</Typography>}
            </Box>
        </Container>
    );
};

export default CreateReport;
