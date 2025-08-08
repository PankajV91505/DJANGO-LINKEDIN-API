import React from "react";
import JobList from "../components/JobList";

const Home = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-700 text-white p-5 text-center text-2xl font-bold shadow-md">
        LinkedIn Job Scraper Dashboard
      </header>
      <main className="max-w-4xl mx-auto p-4">
        <JobList />
      </main>
    </div>
  );
};

export default Home;
