using Supabase.Postgrest.Attributes;
using Supabase.Postgrest.Models;

namespace Minesweeper.Web.Models;

[Table("scores")]
public class Score : BaseModel
{
    [PrimaryKey("id")]
    public int Id { get; set; }

    [Column("player_name")]
    public string PlayerName { get; set; } = string.Empty;

    [Column("difficulty")]
    public string Difficulty { get; set; } = string.Empty;

    [Column("time_seconds")]
    public int TimeSeconds { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; }
}
