// src/components/JobsList.jsx
import React, { useEffect, useState } from "react";
import Loader from "./Loader";
import JobForm from "./JobForm";

const JobsList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobIndex, setSelectedJobIndex] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingJob, setEditingJob] = useState(null);

  const BASE_URL = "http://127.0.0.1:8000/jobs/";

  useEffect(() => {
    fetchJobs(currentPage);
  }, [currentPage]);

  // Fetch jobs from backend
  const fetchJobs = async (page = 1) => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}?page=${page}`);
      const data = await response.json();

      setJobs(data.results || []);
      setHasNextPage(data.next !== null);

      // Calculate total pages based on count
      if (data.count && data.results?.length) {
        setTotalPages(Math.ceil(data.count / data.results.length));
      }
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  // Delete a job
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this job?")) return;
    try {
      await fetch(`${BASE_URL}${id}/`, { method: "DELETE" });
      fetchJobs(currentPage);
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  // Save or update job
  const handleSave = async (job) => {
    try {
      const method = editingJob ? "PUT" : "POST";
      const url = editingJob ? `${BASE_URL}${editingJob.id}/` : BASE_URL;

      await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(job),
      });

      setShowForm(false);
      setEditingJob(null);
      fetchJobs(currentPage);
    } catch (err) {
      console.error("Save failed", err);
    }
  };

  // Filter and sort jobs by scraped_date
  const filteredJobs = jobs
    .filter((job) =>
      [job.title, job.company, job.location].some((field) =>
        field.toLowerCase().includes(searchQuery.toLowerCase())
      )
    )
    .sort((a, b) => new Date(b.scraped_date) - new Date(a.scraped_date));

  return (
    <div className="p-6 bg-white text-black">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold">🧠 Python Developer Jobs</h1>
        <button
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          onClick={() => {
            setEditingJob(null);
            setShowForm(true);
          }}
        >
          ➕ Add Job
        </button>
      </div>

      {/* Add / Edit Form */}
      {showForm && (
        <JobForm
          initialData={editingJob}
          onCancel={() => {
            setShowForm(false);
            setEditingJob(null);
          }}
          onSave={handleSave}
        />
      )}

      {/* Search */}
      <input
        type="text"
        placeholder="Search by title, company, or location..."
        className="w-full p-2 border rounded mb-4 text-black"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />

      {/* Job List */}
      {loading ? (
        <Loader />
      ) : filteredJobs.length === 0 ? (
        <p>No jobs found.</p>
      ) : (
        <div className="space-y-4">
          {filteredJobs.map((job, index) => (
            <div
              key={job.id || index}
              className="p-4 rounded shadow bg-gray-100 relative"
            >
              <div
                className="cursor-pointer"
                onClick={() =>
                  setSelectedJobIndex(index === selectedJobIndex ? null : index)
                }
              >
                <h2 className="text-xl font-semibold">{job.title}</h2>
                <p className="text-gray-600">
                  {job.company} • {job.location} • {job.time_posted}
                </p>
              </div>

              {selectedJobIndex === index && (
                <div className="mt-3 text-gray-700 whitespace-pre-wrap">
                  {job.description}
                </div>
              )}

              <div className="absolute top-2 right-2 space-x-2">
                <button
                  onClick={() => {
                    setEditingJob(job);
                    setShowForm(true);
                  }}
                  className="text-sm bg-yellow-400 px-3 py-1 rounded"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(job.id)}
                  className="text-sm bg-red-500 text-white px-3 py-1 rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div className="flex justify-between items-center mt-6">
        <button
          onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className={`px-4 py-2 rounded ${
            currentPage === 1
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600 text-white"
          }`}
        >
          Prev
        </button>
        <span>
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={() => setCurrentPage((prev) => prev + 1)}
          disabled={!hasNextPage}
          className={`px-4 py-2 rounded ${
            !hasNextPage
              ? "bg-gray-300 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600 text-white"
          }`}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default JobsList;
