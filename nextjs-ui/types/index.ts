export interface Repository {
  id: string
  name: string
  description: string
  language: string
  stars: number
  forks: number
  topics: string[]
  license: string
  size: number
  url: string
}

export interface UserStory {
  id: number
  title: string
  description: string
  acceptanceCriteria: string[]
  priority: 'Low' | 'Medium' | 'High' | 'Critical'
  effort: 'Low' | 'Medium' | 'High' | 'Very High'
  tags: string[]
}

export interface SystemArchitecture {
  systemDiagram: string
  apiFlowDiagram: string
  componentDiagram: string
  dataFlowDiagram: string
}

export interface ApiAnalysis {
  endpoints: string[]
  externalServices: string[]
  authenticationMethods: string[]
  websocketEvents: string[]
}

export interface TechnicalDeepDive {
  technologyStack: {
    backend: string[]
    database: string[]
    storage: string[]
    monitoring: string[]
  }
  buildSystem: {
    packageManager: string
    buildBackend: string
    taskRunner: string
    containerization: string
  }
  performanceOptimizations: string[]
  securityFeatures: string[]
}

export interface AnalysisResult {
  repository: Repository
  analysisDate: Date
  userStories: UserStory[]
  systemArchitecture?: SystemArchitecture
  apiAnalysis?: ApiAnalysis
  technicalDeepDive?: TechnicalDeepDive
  comprehensiveReport?: string
}
