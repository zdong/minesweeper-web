using Minesweeper.Web.Models;
using Supabase;

namespace Minesweeper.Web.Services;

public class ScoreService
{
    private readonly Supabase.Client _client;

    public ScoreService(string supabaseUrl, string supabaseKey)
    {
        var options = new SupabaseOptions
        {
            AutoRefreshToken = false,
            AutoConnectRealtime = false
        };
        _client = new Supabase.Client(supabaseUrl, supabaseKey, options);
    }

    public async Task<bool> SaveScoreAsync(string playerName, string difficulty, int timeSeconds)
    {
        try
        {
            var score = new Score
            {
                PlayerName = playerName,
                Difficulty = difficulty,
                TimeSeconds = timeSeconds,
                CreatedAt = DateTime.UtcNow
            };

            await _client.From<Score>().Insert(score);
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error saving score: {ex.Message}");
            return false;
        }
    }

    public async Task<List<Score>> GetDailyTopScoresAsync(string difficulty, int limit = 10)
    {
        try
        {
            var today = DateTime.UtcNow.Date;
            var response = await _client.From<Score>()
                .Filter("difficulty", Supabase.Postgrest.Constants.Operator.Equals, difficulty)
                .Filter("created_at", Supabase.Postgrest.Constants.Operator.GreaterThanOrEqual, today.ToString("yyyy-MM-dd"))
                .Order("time_seconds", Supabase.Postgrest.Constants.Ordering.Ascending)
                .Limit(limit)
                .Get();

            return response.Models;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting daily scores: {ex.Message}");
            return new List<Score>();
        }
    }

    public async Task<List<Score>> GetWeeklyTopScoresAsync(string difficulty, int limit = 10)
    {
        try
        {
            var weekStart = DateTime.UtcNow.Date.AddDays(-(int)DateTime.UtcNow.DayOfWeek);
            var response = await _client.From<Score>()
                .Filter("difficulty", Supabase.Postgrest.Constants.Operator.Equals, difficulty)
                .Filter("created_at", Supabase.Postgrest.Constants.Operator.GreaterThanOrEqual, weekStart.ToString("yyyy-MM-dd"))
                .Order("time_seconds", Supabase.Postgrest.Constants.Ordering.Ascending)
                .Limit(limit)
                .Get();

            return response.Models;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting weekly scores: {ex.Message}");
            return new List<Score>();
        }
    }

    public async Task<List<Score>> GetAllTimeTopScoresAsync(string difficulty, int limit = 10)
    {
        try
        {
            var response = await _client.From<Score>()
                .Filter("difficulty", Supabase.Postgrest.Constants.Operator.Equals, difficulty)
                .Order("time_seconds", Supabase.Postgrest.Constants.Ordering.Ascending)
                .Limit(limit)
                .Get();

            return response.Models;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error getting all-time scores: {ex.Message}");
            return new List<Score>();
        }
    }
}
