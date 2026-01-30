-- Minesweeper Scoreboard Database Setup
-- Run this in Supabase SQL Editor

-- Create the scores table
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(20) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    time_seconds INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_scores_difficulty ON scores(difficulty);
CREATE INDEX idx_scores_created_at ON scores(created_at);
CREATE INDEX idx_scores_time ON scores(time_seconds);

-- Enable Row Level Security (RLS)
ALTER TABLE scores ENABLE ROW LEVEL SECURITY;

-- Allow anyone to read scores (public leaderboard)
CREATE POLICY "Allow public read access" ON scores
    FOR SELECT USING (true);

-- Allow anyone to insert scores (anonymous submissions)
CREATE POLICY "Allow public insert access" ON scores
    FOR INSERT WITH CHECK (true);

-- Optional: Prevent updates and deletes from public
CREATE POLICY "Deny public update access" ON scores
    FOR UPDATE USING (false);

CREATE POLICY "Deny public delete access" ON scores
    FOR DELETE USING (false);
