// src/components/JobForm.jsx

import React, { useState, useEffect } from "react";

const JobForm = ({ onSave, onCancel, initialData }) => {
  const [job, setJob] = useState({
    title: "",
    company: "",
    location: "",
    time_posted: "",
    description: "",
  });

  useEffect(() => {
    if (initialData) setJob(initialData);
  }, [initialData]);

  const handleChange = (e) => {
    setJob({ ...job, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(job);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white p-4 rounded shadow space-y-4"
    >
      <input
        type="text"
        name="title"
        placeholder="Job Title"
        value={job.title}
        onChange={handleChange}
        required
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="company"
        placeholder="Company"
        value={job.company}
        onChange={handleChange}
        required
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="location"
        placeholder="Location"
        value={job.location}
        onChange={handleChange}
        required
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        name="time_posted"
        placeholder="Time Posted"
        value={job.time_posted}
        onChange={handleChange}
        className="w-full p-2 border rounded"
      />
      <textarea
        name="description"
        placeholder="Description"
        value={job.description}
        onChange={handleChange}
        className="w-full p-2 border rounded h-24"
        required
      />

      <div className="flex gap-3">
        <button
          type="submit"
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded"
        >
          Save
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
        >
          Cancel
        </button>
      </div>
    </form>
  );
};

export default JobForm;
