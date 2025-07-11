import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Settings,
  Dashboard,
  Timeline,
  Storage
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [jobs, setJobs] = useState([]);
  const [models, setModels] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  
  // New job form state
  const [newJob, setNewJob] = useState({
    model_name: '',
    dataset_path: '',
    hyperparameters: {
      learning_rate: 0.001,
      batch_size: 4,
      epochs: 3
    }
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [jobsRes, modelsRes, datasetsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/jobs`),
        axios.get(`${API_BASE_URL}/api/models`),
        axios.get(`${API_BASE_URL}/api/datasets`)
      ]);
      
      setJobs(jobsRes.data);
      setModels(modelsRes.data);
      setDatasets(datasetsRes.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch data. Make sure the API is running.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const createJob = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/jobs`, newJob);
      setJobs([...jobs, response.data]);
      setNewJob({
        model_name: '',
        dataset_path: '',
        hyperparameters: {
          learning_rate: 0.001,
          batch_size: 4,
          epochs: 3
        }
      });
      setError('');
    } catch (err) {
      setError('Failed to create training job.');
      console.error('Error creating job:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const menuItems = [
    { text: 'Dashboard', icon: <Dashboard /> },
    { text: 'Training Jobs', icon: <Timeline /> },
    { text: 'Models', icon: <Storage /> },
    { text: 'Settings', icon: <Settings /> }
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <Settings />
          </IconButton>
          <Typography variant="h6" noWrap component="div">
            LLM Trainer Platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        sx={{
          width: 240,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 240,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            {menuItems.map((item) => (
              <ListItem button key={item.text}>
                <ListItemIcon>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        
        <Container maxWidth="lg">
          <Typography variant="h4" gutterBottom sx={{ mt: 2, mb: 4 }}>
            Train Your Own LLM
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            {/* Create New Job */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Create New Training Job
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Model</InputLabel>
                    <Select
                      value={newJob.model_name}
                      onChange={(e) => setNewJob({...newJob, model_name: e.target.value})}
                    >
                      {models.map((model) => (
                        <MenuItem key={model.name} value={model.name}>
                          {model.name} ({model.parameters})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel>Dataset</InputLabel>
                    <Select
                      value={newJob.dataset_path}
                      onChange={(e) => setNewJob({...newJob, dataset_path: e.target.value})}
                    >
                      {datasets.map((dataset) => (
                        <MenuItem key={dataset.name} value={dataset.name}>
                          {dataset.name} ({dataset.size})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    label="Learning Rate"
                    type="number"
                    value={newJob.hyperparameters.learning_rate}
                    onChange={(e) => setNewJob({
                      ...newJob,
                      hyperparameters: {
                        ...newJob.hyperparameters,
                        learning_rate: parseFloat(e.target.value)
                      }
                    })}
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Batch Size"
                    type="number"
                    value={newJob.hyperparameters.batch_size}
                    onChange={(e) => setNewJob({
                      ...newJob,
                      hyperparameters: {
                        ...newJob.hyperparameters,
                        batch_size: parseInt(e.target.value)
                      }
                    })}
                    sx={{ mb: 2 }}
                  />

                  <TextField
                    fullWidth
                    label="Epochs"
                    type="number"
                    value={newJob.hyperparameters.epochs}
                    onChange={(e) => setNewJob({
                      ...newJob,
                      hyperparameters: {
                        ...newJob.hyperparameters,
                        epochs: parseInt(e.target.value)
                      }
                    })}
                    sx={{ mb: 2 }}
                  />

                  <Button
                    variant="contained"
                    onClick={createJob}
                    disabled={loading || !newJob.model_name || !newJob.dataset_path}
                    startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                    fullWidth
                  >
                    Start Training
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            {/* Training Jobs */}
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                      Training Jobs
                    </Typography>
                    <IconButton onClick={fetchData} disabled={loading}>
                      <Refresh />
                    </IconButton>
                  </Box>

                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                      <CircularProgress />
                    </Box>
                  ) : jobs.length === 0 ? (
                    <Typography color="textSecondary" align="center">
                      No training jobs yet. Create your first job!
                    </Typography>
                  ) : (
                    <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
                      {jobs.map((job) => (
                        <Card key={job.id} sx={{ mb: 1, p: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            {job.model_name}
                          </Typography>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            Dataset: {job.dataset_path}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography
                              variant="caption"
                              color={getStatusColor(job.status)}
                              sx={{ fontWeight: 'bold' }}
                            >
                              {job.status.toUpperCase()}
                            </Typography>
                            <Typography variant="caption" color="textSecondary">
                              {new Date(job.created_at).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </Card>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}

export default App;