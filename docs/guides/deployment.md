# Deployment Guide

The repository includes API, worker and dashboard containers. Configure environment variables through deployment secrets rather than committing `.env` files. MongoDB, PostgreSQL and vector storage can be introduced behind the existing abstractions.
