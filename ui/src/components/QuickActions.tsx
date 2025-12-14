import { FileText, Plane, CreditCard, Car, Building2, Users } from 'lucide-react';

interface QuickActionsProps {
  onSelectQuery: (query: string) => void;
  isLoading: boolean;
}

const quickActions = [
  { icon: Plane, label: 'Passport Info', query: 'How do I apply for a passport?' },
  { icon: FileText, label: 'Citizenship', query: 'Tell me about citizenship certificates' },
  { icon: CreditCard, label: 'Tax Filing', query: 'How do I file my taxes?' },
  { icon: Car, label: 'Driving License', query: 'How to get a driving license?' },
  { icon: Building2, label: 'Business Registration', query: 'How do I register a business?' },
  { icon: Users, label: 'Social Security', query: 'What are the social security benefits?' },
];

export function QuickActions({ onSelectQuery, isLoading }: QuickActionsProps) {
  return (
    <div className="border-t border-gray-200 bg-gray-50 p-4">
      <div className="max-w-4xl mx-auto">
        <p className="text-sm text-gray-600 mb-3">Quick Actions:</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {quickActions.map((action) => (
            <button
              key={action.label}
              onClick={() => onSelectQuery(action.query)}
              disabled={isLoading}
              className="flex flex-col items-center gap-2 p-3 bg-white border border-gray-300 rounded-lg hover:border-blue-600 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <action.icon className="size-5 text-blue-600" />
              <span className="text-xs text-center">{action.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
