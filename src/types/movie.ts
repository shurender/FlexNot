export interface Movie {
  id: number;
  title: string;
  overview: string;
  poster_path: string;
  backdrop_path: string;
  release_date: string;
  vote_average: number;
  vote_count: number;
  genre_ids: number[];
  runtime?: number;
  director?: string;
  cast?: string[];
  trailer_url?: string;
  isNew?: boolean;
  country?: string;
}

export interface Genre {
  id: number;
  name: string;
}

export interface User {
  id: string;
  name: string;
  watchlist: number[];
  ratings: Record<number, number>;
}