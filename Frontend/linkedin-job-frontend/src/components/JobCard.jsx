import React, { useState } from "react";

const JobCard = ({ job }) => {
  const [showDescription, setShowDescription] = useState(false);

  return (
    <div className="p-5 bg-white border rounded-xl shadow-md hover:shadow-lg transition space-y-3">
      <div>
        <h2 className="text-xl font-semibold text-blue-800">{job.title}</h2>
        <p className="text-sm text-gray-700 font-medium">{job.company}</p>
        <p className="text-sm text-gray-500">
          {job.location} • {job.time_posted}
        </p>
      </div>

      <button
        onClick={() => setShowDescription((prev) => !prev)}
        className="text-sm text-blue-600 hover:underline"
      >
        {showDescription ? "Hide Description ▲" : "View Description ▼"}
      </button>

      {showDescription && (
        <p className="text-gray-800 text-sm whitespace-pre-line border-t pt-3">
          {job.description}
        </p>
      )}
    </div>
  );
};

export default JobCard;
