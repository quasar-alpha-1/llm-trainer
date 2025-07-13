import React from 'react';
import { useParams } from 'react-router-dom';

function JobDetail() {
  const { id } = useParams();
  return <div><h1>Job Detail</h1><p>Details, logs, and metrics for job ID: {id}</p></div>;
}

export default JobDetail;