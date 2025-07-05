console.log("🚧 Starting GraphQL server...");

const express = require("express");
const { ApolloServer } = require("@apollo/server");
const { expressMiddleware } = require("@apollo/server/express4");
const cors = require("cors");
const fs = require("fs");
const dotenv = require("dotenv");

// Load env
dotenv.config();

// Load schema
const typeDefs = fs.readFileSync("./schema.graphql", { encoding: "utf-8" });

// Load resolvers
const matchResolver = require("./resolvers/matchResolver");
const weatherResolver = require("./resolvers/weatherResolver");
const newsResolver = require("./resolvers/newsResolver");

// Combine resolvers
const resolvers = {
  Query: {
    ...matchResolver.Query,
    ...weatherResolver.Query,
    ...newsResolver.Query,
  },
};

async function startServer() {
  const app = express();
  const server = new ApolloServer({ typeDefs, resolvers });

  await server.start();

  app.use(cors());
  app.use(express.json()); // 💥 Must be before Apollo middleware
  app.use("/", expressMiddleware(server, {
    context: async () => ({
      CRICAPI_KEY: process.env.CRICAPI_KEY,
      OPENWEATHER_KEY: process.env.OPENWEATHER_KEY,
      NEWSAPI_KEY: process.env.NEWSAPI_KEY,
    }),
  }));

  const PORT = 4000;
  app.listen(PORT, () => {
    console.log(`🚀 Server running at http://localhost:${PORT}/`);
  });
}

startServer().catch(err => {
  console.error("❌ Server error:", err);
});
