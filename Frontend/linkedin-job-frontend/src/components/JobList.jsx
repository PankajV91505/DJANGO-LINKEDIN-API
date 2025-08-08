import React, { useEffect, useState } from "react";
import Loader from "./Loader";

const JobsList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobIndex, setSelectedJobIndex] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [totalPages, setTotalPages] = useState(1);

  const BASE_URL = "http://127.0.0.1:8000/jobs/";

  useEffect(() => {
    fetchJobs(currentPage);

    const interval = setInterval(() => {
      fetchJobs(currentPage);
    }, 30000);

    return () => clearInterval(interval);
  }, [currentPage]);

  const fetchJobs = async (page = 1) => {
    setLoading(true);
    try {
      const response = await fetch(`${BASE_URL}?page=${page}`);
      const data = await response.json();
      const sortedJobs = (data.results || []).sort((a, b) =>
        a.time_posted < b.time_posted ? 1 : -1
      );
      setJobs(sortedJobs);
      setHasNextPage(data.next !== null);
      setTotalPages(Math.ceil(data.count / 10)); // assuming 10 results per page
    } catch (error) {
      console.error("Error fetching jobs:", error);
    } finally {
      setLoading(false);
    }
  };

  const filteredJobs = jobs.filter(
    (job) =>
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.company.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.location.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6 bg-white text-black min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-center mb-4">🧠 Python Developer Jobs</h1>
        <input
          type="text"
          placeholder="Search by title, company, or location..."
          className="w-full p-2 border border-gray-300 rounded"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {loading ? (
        <Loader />
      ) : filteredJobs.length === 0 ? (
        <p className="text-center text-gray-600">No jobs found.</p>
      ) : (
        <div className="space-y-4">
          {filteredJobs.map((job, index) => (
            <div key={index} className="p-4 rounded shadow bg-gray-100">
              <div
                className="cursor-pointer"
                onClick={() =>
                  setSelectedJobIndex(index === selectedJobIndex ? null : index)
                }
              >
                <h2 className="text-xl font-semibold">{job.title}</h2>
                <p className="text-gray-700">
                  {job.company} • {job.location} • {job.time_posted}
                </p>
              </div>

              {selectedJobIndex === index && (
                <div className="mt-3 text-gray-800 whitespace-pre-wrap">
                  {job.description}
                </div>
              )}
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

        <span className="text-gray-800">
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
