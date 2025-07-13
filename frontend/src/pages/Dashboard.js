import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getJobs, getModels, getDatasets } from '../api';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Button, Grid, CircularProgress, Alert } from '@mui/material';

function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [models, setModels] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    setLoading(true);
    Promise.all([getJobs(), getModels(), getDatasets()])
      .then(([jobsData, modelsData, datasetsData]) => {
        setJobs(jobsData);
        setModels(modelsData);
        setDatasets(datasetsData);
        setError('');
      })
      .catch(() => setError('Failed to fetch dashboard data'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div style={{ textAlign: 'center', marginTop: 40 }}><CircularProgress /></div>;
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <div>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      <Grid container spacing={3} sx={{ marginBottom: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Recent Jobs</Typography>
              <List>
                {jobs.slice(0, 5).map(job => (
                  <ListItem key={job.id} component={Link} to={`/jobs/${job.id}`} button>
                    <ListItemText primary={`${job.model_name || job.model} (${job.status})`} />
                  </ListItem>
                ))}
                {jobs.length === 0 && <ListItem><ListItemText primary="No jobs yet" /></ListItem>}
              </List>
              <Button component={Link} to="/jobs" variant="outlined" size="small">View all jobs</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Models</Typography>
              <List>
                {models.slice(0, 5).map(model => (
                  <ListItem key={model.id || model.name}><ListItemText primary={model.name} /></ListItem>
                ))}
                {models.length === 0 && <ListItem><ListItemText primary="No models yet" /></ListItem>}
              </List>
              <Button component={Link} to="/local-models" variant="outlined" size="small">View all models</Button>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Datasets</Typography>
              <List>
                {datasets.slice(0, 5).map(ds => (
                  <ListItem key={ds.id || ds.name}><ListItemText primary={ds.name} /></ListItem>
                ))}
                {datasets.length === 0 && <ListItem><ListItemText primary="No datasets yet" /></ListItem>}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      <Button component={Link} to="/new-job" variant="contained" color="primary">Create New Training Job</Button>
    </div>
  );
}

export default Dashboard;