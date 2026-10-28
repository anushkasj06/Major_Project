db = db.getSiblingDB('arambh');

db.createCollection('users');
db.createCollection('conversations');
db.createCollection('colleges');
db.createCollection('documents');
db.createCollection('crawler_jobs');
db.createCollection('query_analytics');

// Indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.conversations.createIndex({ session_id: 1, user_id: 1 });
db.conversations.createIndex({ user_id: 1, updated_at: -1 });
db.colleges.createIndex({ name: "text", "location.city": "text" });
db.colleges.createIndex({ college_type: 1 });
db.documents.createIndex({ status: 1 });
db.documents.createIndex({ college_id: 1 });
db.crawler_jobs.createIndex({ status: 1, created_at: -1 });
db.query_analytics.createIndex({ created_at: -1 });
db.query_analytics.createIndex({ session_id: 1 });

// Seed admin user (password: admin123)
db.users.insertOne({
  name: "Admin",
  email: "admin@arambh.local",
  hashed_password: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lew9pDqlkKlRCm9jK",
  role: "admin",
  is_active: true,
  preferred_language: "en",
  created_at: new Date()
});

// Seed sample colleges
db.colleges.insertMany([
  {
    name: "College of Engineering Pune (COEP)",
    short_name: "COEP",
    college_type: "engineering",
    location: { city: "Pune", district: "Pune", state: "Maharashtra", pincode: "411005" },
    website: "https://www.coep.org.in",
    established_year: 1854,
    affiliation: "Savitribai Phule Pune University",
    approval: "AICTE",
    branches: [
      { name: "Computer Engineering", code: "CE", seats: 120 },
      { name: "Mechanical Engineering", code: "ME", seats: 60 },
      { name: "Electronics Engineering", code: "ENTC", seats: 60 },
      { name: "Civil Engineering", code: "Civil", seats: 60 }
    ],
    fees: { annual_tuition: 95000, hostel_annual: 60000, other_fees: 15000 },
    placements: { avg_package_lpa: 8.5, highest_package_lpa: 42, placement_percentage: 88 },
    cutoffs: {
      "2024": { general: { CE: 98.5, ME: 96.2, ENTC: 97.8 }, obc: { CE: 97.2, ME: 94.1 } }
    },
    ranking: { nirf: 45, state_rank: 2 },
    created_at: new Date(), updated_at: new Date()
  },
  {
    name: "Veermata Jijabai Technological Institute (VJTI)",
    short_name: "VJTI",
    college_type: "engineering",
    location: { city: "Mumbai", district: "Mumbai", state: "Maharashtra", pincode: "400019" },
    website: "https://www.vjti.ac.in",
    established_year: 1887,
    affiliation: "Mumbai University",
    approval: "AICTE",
    branches: [
      { name: "Computer Engineering", code: "CE", seats: 60 },
      { name: "Electronics Engineering", code: "ETRX", seats: 60 },
      { name: "Mechanical Engineering", code: "MECH", seats: 60 }
    ],
    fees: { annual_tuition: 92000, hostel_annual: 55000, other_fees: 12000 },
    placements: { avg_package_lpa: 9.2, highest_package_lpa: 48, placement_percentage: 91 },
    cutoffs: {
      "2024": { general: { CE: 99.1, ETRX: 98.4 } }
    },
    ranking: { nirf: 38, state_rank: 1 },
    created_at: new Date(), updated_at: new Date()
  }
]);

print("✅ Arambh database initialized with seed data");
