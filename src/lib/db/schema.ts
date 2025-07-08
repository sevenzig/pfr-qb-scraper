// drizzle/schema.ts - Drizzle ORM Schema for NFL QB Data
import { pgTable, bigserial, varchar, integer, decimal, timestamp, boolean, text, date, check, primaryKey, foreignKey } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// Player Master Table (uses PFR unique ID as primary key)
export const players = pgTable('players', {
  pfrId: varchar('pfr_id', { length: 20 }).primaryKey(), // PFR unique ID (e.g., 'burrjo01')
  playerName: varchar('player_name', { length: 100 }).notNull(),
  firstName: varchar('first_name', { length: 50 }),
  lastName: varchar('last_name', { length: 50 }),
  position: varchar('position', { length: 5 }).default('QB'),
  heightInches: integer('height_inches'),
  weightLbs: integer('weight_lbs'),
  birthDate: date('birth_date'),
  age: integer('age'),
  college: varchar('college', { length: 100 }),
  draftYear: integer('draft_year'),
  draftRound: integer('draft_round'),
  draftPick: integer('draft_pick'),
  pfrUrl: varchar('pfr_url', { length: 255 }).notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
}, (table) => ({
  validHeight: check('valid_height', sql`${table.heightInches} IS NULL OR (${table.heightInches} > 60 AND ${table.heightInches} < 84)`),
  validWeight: check('valid_weight', sql`${table.weightLbs} IS NULL OR (${table.weightLbs} > 150 AND ${table.weightLbs} < 350)`),
  validAge: check('valid_age', sql`${table.age} IS NULL OR (${table.age} > 15 AND ${table.age} < 50)`),
  validDraftYear: check('valid_draft_year', sql`${table.draftYear} IS NULL OR (${table.draftYear} >= 1936 AND ${table.draftYear} <= 2030)`),
  validDraftRound: check('valid_draft_round', sql`${table.draftRound} IS NULL OR (${table.draftRound} >= 1 AND ${table.draftRound} <= 10)`),
  validDraftPick: check('valid_draft_pick', sql`${table.draftPick} IS NULL OR (${table.draftPick} >= 1 AND ${table.draftPick} <= 300)`),
}));

// Team Master Table
export const teams = pgTable('teams', {
  teamCode: varchar('team_code', { length: 3 }).primaryKey(),
  teamName: varchar('team_name', { length: 100 }).notNull(),
  city: varchar('city', { length: 50 }).notNull(),
  conference: varchar('conference', { length: 3 }),
  division: varchar('division', { length: 10 }),
  foundedYear: integer('founded_year'),
  stadiumName: varchar('stadium_name', { length: 100 }),
  stadiumCapacity: integer('stadium_capacity'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
});

// Basic QB Statistics Table (season totals)
export const qbBasicStats = pgTable('qb_basic_stats', {
  pfrId: varchar('pfr_id', { length: 20 }).notNull(),
  season: integer('season').notNull(),
  team: varchar('team', { length: 3 }).notNull(),
  gamesPlayed: integer('games_played').default(0),
  gamesStarted: integer('games_started').default(0),
  completions: integer('completions').default(0),
  attempts: integer('attempts').default(0),
  completionPct: decimal('completion_pct', { precision: 5, scale: 2 }),
  passYards: integer('pass_yards').default(0),
  passTds: integer('pass_tds').default(0),
  interceptions: integer('interceptions').default(0),
  longestPass: integer('longest_pass').default(0),
  rating: decimal('rating', { precision: 5, scale: 2 }),
  sacks: integer('sacks').default(0),
  sackYards: integer('sack_yards').default(0),
  netYardsPerAttempt: decimal('net_yards_per_attempt', { precision: 4, scale: 2 }),
  scrapedAt: timestamp('scraped_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
}, (table) => ({
  pk: primaryKey({ columns: [table.pfrId, table.season] }),
  fkPlayer: foreignKey({ columns: [table.pfrId], foreignColumns: [players.pfrId] }),
  fkTeam: foreignKey({ columns: [table.team], foreignColumns: [teams.teamCode] }),
  seasonCheck: check('season_check', sql`${table.season} >= 1920 AND ${table.season} <= 2030`),
  ratingCheck: check('rating_check', sql`${table.rating} >= 0 AND ${table.rating} <= 158.3`),
  completionPctCheck: check('completion_pct_check', sql`${table.completionPct} >= 0 AND ${table.completionPct} <= 100`),
  validCompletionRatio: check('valid_completion_ratio', sql`${table.attempts} = 0 OR ${table.completions} <= ${table.attempts}`),
  validGamesStarted: check('valid_games_started', sql`${table.gamesStarted} <= ${table.gamesPlayed}`),
}));

// Advanced QB Statistics Table (advanced metrics)
export const qbAdvancedStats = pgTable('qb_advanced_stats', {
  pfrId: varchar('pfr_id', { length: 20 }).notNull(),
  season: integer('season').notNull(),
  qbr: decimal('qbr', { precision: 5, scale: 2 }),
  adjustedNetYardsPerAttempt: decimal('adjusted_net_yards_per_attempt', { precision: 4, scale: 2 }),
  fourthQuarterComebacks: integer('fourth_quarter_comebacks').default(0),
  gameWinningDrives: integer('game_winning_drives').default(0),
  scrapedAt: timestamp('scraped_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
}, (table) => ({
  pk: primaryKey({ columns: [table.pfrId, table.season] }),
  fkPlayer: foreignKey({ columns: [table.pfrId], foreignColumns: [players.pfrId] }),
  seasonCheck: check('season_check', sql`${table.season} >= 1920 AND ${table.season} <= 2030`),
  qbrCheck: check('qbr_check', sql`${table.qbr} >= 0 AND ${table.qbr} <= 100`),
}));

// QB Splits Statistics Table (situational splits)
export const qbSplits = pgTable('qb_splits', {
  id: bigserial('id', { mode: 'number' }).primaryKey(),
  pfrId: varchar('pfr_id', { length: 20 }).notNull(),
  season: integer('season').notNull(),
  splitType: varchar('split_type', { length: 50 }).notNull(),
  splitCategory: varchar('split_category', { length: 100 }).notNull(),
  games: integer('games').default(0),
  completions: integer('completions').default(0),
  attempts: integer('attempts').default(0),
  completionPct: decimal('completion_pct', { precision: 5, scale: 2 }),
  passYards: integer('pass_yards').default(0),
  passTds: integer('pass_tds').default(0),
  interceptions: integer('interceptions').default(0),
  rating: decimal('rating', { precision: 5, scale: 2 }),
  sacks: integer('sacks').default(0),
  sackYards: integer('sack_yards').default(0),
  netYardsPerAttempt: decimal('net_yards_per_attempt', { precision: 4, scale: 2 }),
  scrapedAt: timestamp('scraped_at', { withTimezone: true }).defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow(),
  // Additional fields for comprehensive QB splits data
  rushAttempts: integer('rush_attempts').default(0),
  rushYards: integer('rush_yards').default(0),
  rushTds: integer('rush_tds').default(0),
  fumbles: integer('fumbles').default(0),
  fumblesLost: integer('fumbles_lost').default(0),
  fumblesForced: integer('fumbles_forced').default(0),
  fumblesRecovered: integer('fumbles_recovered').default(0),
  fumbleRecoveryYards: integer('fumble_recovery_yards').default(0),
  fumbleRecoveryTds: integer('fumble_recovery_tds').default(0),
  incompletions: integer('incompletions').default(0),
  wins: integer('wins').default(0),
  losses: integer('losses').default(0),
  ties: integer('ties').default(0),
  attemptsPerGame: decimal('attempts_per_game', { precision: 4, scale: 2 }),
  yardsPerGame: decimal('yards_per_game', { precision: 6, scale: 2 }),
  rushAttemptsPerGame: decimal('rush_attempts_per_game', { precision: 4, scale: 2 }),
  rushYardsPerGame: decimal('rush_yards_per_game', { precision: 6, scale: 2 }),
  totalTds: integer('total_tds').default(0),
  points: integer('points').default(0),
}, (table) => ({
  fkPlayer: foreignKey({ columns: [table.pfrId], foreignColumns: [players.pfrId] }),
  seasonCheck: check('season_check', sql`${table.season} >= 1920 AND ${table.season} <= 2030`),
  ratingCheck: check('rating_check', sql`${table.rating} >= 0 AND ${table.rating} <= 158.3`),
  completionPctCheck: check('completion_pct_check', sql`${table.completionPct} >= 0 AND ${table.completionPct} <= 100`),
  validSplitCompletionRatio: check('valid_split_completion_ratio', sql`${table.attempts} = 0 OR ${table.completions} <= ${table.attempts}`),
  validFumblesLost: check('valid_fumbles_lost', sql`${table.fumblesLost} <= ${table.fumbles}`),
  validFumblesRecovered: check('valid_fumbles_recovered', sql`${table.fumblesRecovered} <= ${table.fumbles}`),
  validTotalTds: check('valid_total_tds', sql`${table.totalTds} >= (${table.passTds} + ${table.rushTds} + ${table.fumbleRecoveryTds})`),
}));

// Game Log Table (for individual game performance)
export const qbGameLog = pgTable('qb_game_log', {
  id: bigserial('id', { mode: 'number' }).primaryKey(),
  pfrId: varchar('pfr_id', { length: 20 }).notNull(),
  season: integer('season').notNull(),
  week: integer('week').notNull(),
  gameDate: date('game_date').notNull(),
  opponent: varchar('opponent', { length: 3 }).notNull(),
  homeAway: varchar('home_away', { length: 4 }),
  result: varchar('result', { length: 10 }),
  completions: integer('completions').default(0),
  attempts: integer('attempts').default(0),
  completionPct: decimal('completion_pct', { precision: 5, scale: 2 }),
  passYards: integer('pass_yards').default(0),
  passTds: integer('pass_tds').default(0),
  interceptions: integer('interceptions').default(0),
  rating: decimal('rating', { precision: 5, scale: 2 }),
  sacks: integer('sacks').default(0),
  sackYards: integer('sack_yards').default(0),
  rushAttempts: integer('rush_attempts').default(0),
  rushYards: integer('rush_yards').default(0),
  rushTds: integer('rush_tds').default(0),
  fumbles: integer('fumbles').default(0),
  fumblesLost: integer('fumbles_lost').default(0),
  gameWinningDrive: boolean('game_winning_drive').default(false),
  fourthQuarterComeback: boolean('fourth_quarter_comeback').default(false),
  weather: varchar('weather', { length: 10 }),
  temperature: integer('temperature'),
  windSpeed: integer('wind_speed'),
  fieldSurface: varchar('field_surface', { length: 10 }),
  scrapedAt: timestamp('scraped_at', { withTimezone: true }).defaultNow(),
}, (table) => ({
  fkPlayer: foreignKey({ columns: [table.pfrId], foreignColumns: [players.pfrId] }),
  fkOpponent: foreignKey({ columns: [table.opponent], foreignColumns: [teams.teamCode] }),
  seasonCheck: check('season_check', sql`${table.season} >= 1920 AND ${table.season} <= 2030`),
  weekCheck: check('week_check', sql`${table.week} >= 1 AND ${table.week} <= 22`),
  ratingCheck: check('rating_check', sql`${table.rating} >= 0 AND ${table.rating} <= 158.3`),
  validGameCompletionRatio: check('valid_game_completion_ratio', sql`${table.attempts} = 0 OR ${table.completions} <= ${table.attempts}`),
  validFumblesLost: check('valid_fumbles_lost', sql`${table.fumblesLost} <= ${table.fumbles}`),
}));

// Scraping Log Table (for monitoring and audit trail)
export const scrapingLog = pgTable('scraping_log', {
  id: bigserial('id', { mode: 'number' }).primaryKey(),
  sessionId: varchar('session_id', { length: 36 }).notNull(),
  season: integer('season').notNull(),
  startTime: timestamp('start_time', { withTimezone: true }).notNull(),
  endTime: timestamp('end_time', { withTimezone: true }),
  totalRequests: integer('total_requests').default(0),
  successfulRequests: integer('successful_requests').default(0),
  failedRequests: integer('failed_requests').default(0),
  totalPlayers: integer('total_players').default(0),
  totalBasicStats: integer('total_basic_stats').default(0),
  totalAdvancedStats: integer('total_advanced_stats').default(0),
  totalQbSplits: integer('total_qb_splits').default(0),
  errors: text('errors').array(),
  warnings: text('warnings').array(),
  rateLimitViolations: integer('rate_limit_violations').default(0),
  processingTimeSeconds: decimal('processing_time_seconds', { precision: 10, scale: 2 }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow(),
}, (table) => ({
  seasonCheck: check('season_check', sql`${table.season} >= 1920 AND ${table.season} <= 2030`),
  validRequestCounts: check('valid_request_counts', sql`${table.successfulRequests} + ${table.failedRequests} = ${table.totalRequests}`),
}));

// Export table references for relationships
export const playersRelations = {
  basicStats: qbBasicStats,
  advancedStats: qbAdvancedStats,
  splits: qbSplits,
  gameLogs: qbGameLog,
};

export const teamsRelations = {
  basicStats: qbBasicStats,
  gameLogs: qbGameLog,
}; 