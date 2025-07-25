import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  TextField,
  Button,
  Typography,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  Checkbox,
  ListItemText,
  OutlinedInput
} from "@mui/material";
import axios from "axios";

const equipmentOptions = [
  "Parallette Bars", "Suspension Trainer", "Gymnastic Rings", "Dumbbell", "Cable", "Barbell", "EZ Bar", "Stability Ball",
  "Bodyweight", "Landmine", "Superband", "Kettlebell", "Resistance Band", "Weight Plate", "Macebell", "Indian Club",
  "Clubbell", "Pull Up Bar", "Tire", "Trap Bar", "Battle Ropes", "Sliders", "Miniband", "Sandbag", "Bulgarian Bag",
  "Sled", "Heavy Sandbag", "Slam Ball", "Ab Wheel", "Medicine Ball", "Wall Ball"
];

const UpdateUserPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await axios.get(`https://fitfuelcustom.loca.lt/admin/users/${id}`, {
          headers: { "bypass-tunnel-reminder": "true" }
        });

        const fetchedUser = response.data;

        // Ensure equipment is an array
        if (typeof fetchedUser.equipment === "string") {
          fetchedUser.equipment = fetchedUser.equipment
            .split(",")
            .map((e) => e.trim())
            .filter((e) => e);
        }

        setUser(fetchedUser);
      } catch (error) {
        console.error("Error fetching user:", error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchUser();
  }, [id]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setUser((prev) => ({ ...prev, [name]: value }));
  };

  const handleEquipmentChange = (e) => {
    const { value } = e.target;
    setUser((prev) => ({
      ...prev,
      equipment: typeof value === "string" ? value.split(",") : value
    }));
  };

  const handleSubmit = async () => {
    try {
      await axios.put(
        `https://fitfuelcustom.loca.lt/admin/users/${id}`,
        {
          ...user,
          equipment: Array.isArray(user.equipment)
            ? user.equipment.join(", ")
            : user.equipment
        },
        {
          headers: { "bypass-tunnel-reminder": "true" }
        }
      );
      alert("User updated successfully!");
      navigate("/team");
    } catch (error) {
      console.error("Update failed:", error.message);
    }
  };

  const handleCancel = () => {
    navigate("/team");
  };

  if (loading) return <Typography>Loading user...</Typography>;
  if (!user) return <Typography>User not found</Typography>;

  return (
    <Box m={4}>
      <Typography variant="h4" gutterBottom>
        Update User
      </Typography>
      <Box display="flex" flexDirection="column" gap={2} maxWidth="500px">
        <TextField label="Name" name="name" value={user.name || ""} onChange={handleChange} fullWidth />
        <TextField label="Email" name="email" value={user.email || ""} onChange={handleChange} fullWidth />
        <TextField label="Age" name="age" type="number" value={user.age || ""} onChange={handleChange} fullWidth />
        <TextField label="Height (cm)" name="heightCm" type="number" value={user.heightCm || ""} onChange={handleChange} fullWidth />
        <TextField label="Weight (kg)" name="weightKg" type="number" value={user.weightKg || ""} onChange={handleChange} fullWidth />
        <TextField label="Target Weight (kg)" name="targetWeightKg" type="number" value={user.targetWeightKg || ""} onChange={handleChange} fullWidth />

        <FormControl fullWidth>
          <InputLabel>Gender</InputLabel>
          <Select name="gender" value={user.gender || ""} onChange={handleChange} label="Gender">
            <MenuItem value="male">Male</MenuItem>
            <MenuItem value="female">Female</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Goal</InputLabel>
          <Select name="goal" value={user.goal || ""} onChange={handleChange} label="Goal">
            <MenuItem value="fat loss">Fat Loss</MenuItem>
            <MenuItem value="endurance">Endurance</MenuItem>
            <MenuItem value="muscle gain">Muscle Gain</MenuItem>
            <MenuItem value="strength">Strength</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Fitness Level</InputLabel>
          <Select name="fitnessLevel" value={user.fitnessLevel || ""} onChange={handleChange} label="Fitness Level">
            <MenuItem value="beginner">Beginner</MenuItem>
            <MenuItem value="intermediate">Intermediate</MenuItem>
            <MenuItem value="advance">Advance</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Availability (days/week)</InputLabel>
          <Select name="availability" value={user.availability || ""} onChange={handleChange} label="Availability">
            <MenuItem value={3}>3</MenuItem>
            <MenuItem value={4}>4</MenuItem>
            <MenuItem value={5}>5</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Activity Level</InputLabel>
          <Select name="activityLevel" value={user.activityLevel || ""} onChange={handleChange} label="Activity Level">
            <MenuItem value="sedentary">Sedentary</MenuItem>
            <MenuItem value="light">Light</MenuItem>
            <MenuItem value="moderate">Moderate</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="very active">Very Active</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Equipment</InputLabel>
          <Select
            multiple
            value={user.equipment || []}
            onChange={handleEquipmentChange}
            input={<OutlinedInput label="Equipment" />}
            renderValue={(selected) => selected.join(", ")}
          >
            {equipmentOptions.map((item) => (
              <MenuItem key={item} value={item}>
                <Checkbox checked={user.equipment?.includes(item)} />
                <ListItemText primary={item} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button variant="contained" color="primary" onClick={handleSubmit}>
          Save Changes
        </Button>
        <Button variant="outlined" color="error" onClick={handleCancel}>
          Cancel
        </Button>
      </Box>
    </Box>
  );
};

export default UpdateUserPage;
