import React, { useEffect, useState } from "react";
import { Box, Button, useTheme } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import axios from "axios";
import { tokens } from "../../theme";
import Header from "../../components/Header";
import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";
import { useNavigate } from "react-router-dom";

const Team = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [columns, setColumns] = useState([]);

  useEffect(() => {
    async function fetchUsers() {
      try {
        const response = await axios.get(
          "https://fitfuelcustom.loca.lt/admin/users",
          {
            headers: {
              "bypass-tunnel-reminder": "true",
            },
          }
        );

        const data = response.data;

        if (data.length > 0) {
          // Use correct key names (case-sensitive)
          const dynamicColumns = Object.keys(data[0])
            .filter((key) => key !== "passwordHash") // Exclude sensitive field
            .map((key) => ({
              field: key,
              headerName: key
                .replace(/([A-Z])/g, " $1")
                .replace(/^./, (s) => s.toUpperCase()),
              flex: 1,
              minWidth: 150,
            }));

          // Add Actions column with buttons
          dynamicColumns.push({
            field: "actions",
            headerName: "Actions",
            sortable: false,
            width: 200,
            renderCell: (params) => (
              <Box display="flex" gap="10px">
                <Button
                  variant="contained"
                  size="small"
                  color="primary"
                  startIcon={<EditIcon />}
                  onClick={() => navigate(`/update/${params.row.userId}`)} // correct userId key
                >
                  Update
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => handleDelete(params.row.userId)} // delete handler
                >
                  Delete
                </Button>
              </Box>
            ),
          });

          setColumns(dynamicColumns);

          // Assign DataGrid-required `id` field properly
          const usersWithRowId = data.map((user) => ({
            ...user,
            id: user.userId, // Correct lowercase 'userId' as MUI requires 'id'
          }));

          setUsers(usersWithRowId);
        }
      } catch (error) {
        console.error("Error fetching users:", error.message);
      }
    }

    fetchUsers();
  }, [navigate]);

  // ✅ Optional Delete Handler
  const handleDelete = async (userId) => {
    const confirmDelete = window.confirm("Are you sure you want to delete this user?");
    if (!confirmDelete) return;

    try {
      await axios.delete(`https://fitfuelcustom.loca.lt/admin/users/${userId}`, {
        headers: { "bypass-tunnel-reminder": "true" },
      });

      setUsers((prev) => prev.filter((user) => user.userId !== userId));
    } catch (err) {
      console.error("Failed to delete user:", err.message);
    }
  };

  return (
    <Box m="20px">
      <Header title="TEAM" subtitle="Managing the Team Members" />
      <Box
        height="70vh"
        sx={{
          "& .MuiDataGrid-root": { border: "none" },
          "& .MuiDataGrid-cell": { borderBottom: "none" },
          "& .MuiDataGrid-columnHeaders": {
            backgroundColor: colors.blueAccent[700],
            borderBottom: "none",
          },
          "& .MuiDataGrid-virtualScroller": {
            backgroundColor: colors.primary[400],
          },
          "& .MuiDataGrid-footerContainer": {
            borderTop: "none",
            backgroundColor: colors.blueAccent[700],
          },
        }}
      >
        <DataGrid
          rows={users}
          columns={columns}
          getRowId={(row) => row.userId} // Optional but ensures correct mapping
        />
      </Box>
    </Box>
  );
};

export default Team;
