import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getJobs } from '../api';
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, CircularProgress, Typography } from '@mui/material';
import { useSnackbar } from 'notistack';

function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    setLoading(true);
    getJobs()
      .then(data => {
        setJobs(data);
        setError('');
      })
      .catch(err => {
        setError('Failed to fetch jobs');
        enqueueSnackbar('Failed to fetch jobs', { variant: 'error' });
      })
      .finally(() => setLoading(false));
  }, [enqueueSnackbar]);

  if (loading) return <div style={{ textAlign: 'center', marginTop: 40 }}><CircularProgress /></div>;
  if (error) return <Typography color="error" align="center">{error}</Typography>;

  return (
    <div>
      <h1>Jobs</h1>
      <TableContainer component={Paper} sx={{ marginTop: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Model</TableCell>
              <TableCell>Dataset</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.map(job => (
              <TableRow key={job.id}>
                <TableCell><Link to={`/jobs/${job.id}`}>{job.id}</Link></TableCell>
                <TableCell>{job.model_name || job.model}</TableCell>
                <TableCell>{job.dataset_path || job.dataset}</TableCell>
                <TableCell>{job.status}</TableCell>
                <TableCell>{new Date(job.created_at || job.createdAt).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}

export default Jobs;