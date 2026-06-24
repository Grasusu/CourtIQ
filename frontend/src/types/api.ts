export type Team = {
  id: number;
  name: string;
  season: string | null;
  created_at: string;
};

export type Player = {
  id: number;
  team_id: number;
  name: string;
  position: string | null;
  jersey_number: number | null;
  created_at: string;
};

export type UploadResult = {
  team_id: number;
  rows_processed: number;
  games_created: number;
  players_created: number;
  stats_created: number;
  stats_updated: number;
};

export type DemoSeedResult = {
  team_id: number;
  team_name: string;
  player_count: number;
  upload: UploadResult;
};

export type DemoResetResult = {
  deleted_teams: number;
};

export type PlayerGameInsight = {
  game_id: number;
  game_date: string;
  opponent: string;
  points: number;
  rebounds: number;
  assists: number;
  minutes: number;
  true_shooting_percentage: number;
  effective_field_goal_percentage: number;
};

export type PlayerAnalytics = {
  player_id: number;
  player_name: string;
  games_played: number;
  average_minutes: number;
  average_points: number;
  average_rebounds: number;
  average_assists: number;
  points_per_minute: number;
  assist_to_turnover_ratio: number | string;
  true_shooting_percentage: number;
  effective_field_goal_percentage: number;
  consistency_score: number;
  last_five_points: Array<number | null>;
  best_game: PlayerGameInsight | null;
  worst_game: PlayerGameInsight | null;
  summary: string;
};

export type TeamPlayerSummary = {
  player_id: number;
  player_name: string;
  games_played: number;
  average_points: number;
  average_rebounds: number;
  average_assists: number;
  true_shooting_percentage: number;
  effective_field_goal_percentage: number;
};

export type TeamTrendPoint = {
  game_id: number;
  game_date: string;
  opponent: string;
  points: number;
  rebounds: number;
  assists: number;
  turnovers: number;
};

export type TeamAnalytics = {
  team_id: number;
  team_name: string;
  roster_size: number;
  games_played: number;
  average_team_points: number;
  average_team_rebounds: number;
  average_team_assists: number;
  average_team_turnovers: number;
  true_shooting_percentage: number;
  effective_field_goal_percentage: number;
  top_scorers: TeamPlayerSummary[];
  game_trends: TeamTrendPoint[];
  summary: string;
};
