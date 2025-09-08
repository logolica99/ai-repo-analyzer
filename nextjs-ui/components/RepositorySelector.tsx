'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Github, Star, GitFork, Tag, ExternalLink } from 'lucide-react'
import { Repository } from '@/types'

interface RepositorySelectorProps {
  repositories: Repository[]
  selectedRepo: Repository | null
  onSelectRepo: (repo: Repository) => void
  disabled?: boolean
}

export default function RepositorySelector({
  repositories,
  selectedRepo,
  onSelectRepo,
  disabled = false
}: RepositorySelectorProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredRepos = repositories.filter(repo =>
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    repo.language.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="space-y-4">
      {/* Search Input */}
      <div className="relative">
        <input
          type="text"
          placeholder="Search repositories..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          disabled={disabled}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
        />
      </div>

      {/* Repository List */}
      <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
        {filteredRepos.map((repo, index) => (
          <motion.div
            key={repo.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            onClick={() => !disabled && onSelectRepo(repo)}
            className={`p-4 border rounded-lg cursor-pointer transition-all ${
              selectedRepo?.id === repo.id
                ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-2">
                  <Github className="h-4 w-4 text-gray-500 flex-shrink-0" />
                  <h3 className="font-medium text-gray-900 truncate">
                    {repo.name}
                  </h3>
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {repo.description}
                </p>

                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center space-x-1">
                    <Star className="h-3 w-3" />
                    <span>{repo.stars.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <GitFork className="h-3 w-3" />
                    <span>{repo.forks.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span>{repo.language}</span>
                  </div>
                </div>

                <div className="flex items-center space-x-2 mt-2">
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {repo.license}
                  </span>
                  <span className="text-xs text-gray-500">
                    {(repo.size / 1024).toFixed(1)} MB
                  </span>
                </div>

                {repo.topics.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {repo.topics.slice(0, 3).map((topic) => (
                      <span
                        key={topic}
                        className="inline-flex items-center space-x-1 text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded"
                      >
                        <Tag className="h-2 w-2" />
                        <span>{topic}</span>
                      </span>
                    ))}
                    {repo.topics.length > 3 && (
                      <span className="text-xs text-gray-500">
                        +{repo.topics.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredRepos.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <Github className="h-8 w-8 mx-auto mb-2 text-gray-300" />
          <p>No repositories found matching your search.</p>
        </div>
      )}
    </div>
  )
}
