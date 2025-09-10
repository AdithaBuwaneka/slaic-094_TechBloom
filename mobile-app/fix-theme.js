// Quick theme fix script - run with node
const fs = require('fs');
const path = require('path');

const files = [
  'app/(main)/(tabs)/chat.tsx',
  'app/(main)/(tabs)/community.tsx',
  'app/(main)/(tabs)/routes.tsx'
];

const replacements = [
  // Common background replacements
  { from: /className="([^"]*?)bg-gray-50([^"]*?)"/g, to: 'className="$1$2" style={{ backgroundColor: theme.background }}' },
  { from: /className="([^"]*?)bg-white([^"]*?)"/g, to: 'className="$1$2" style={{ backgroundColor: theme.surface }}' },
  
  // Text color replacements
  { from: /className="([^"]*?)text-gray-800([^"]*?)"/g, to: 'className="$1$2" style={{ color: theme.text }}' },
  { from: /className="([^"]*?)text-gray-600([^"]*?)"/g, to: 'className="$1$2" style={{ color: theme.textSecondary }}' },
  { from: /className="([^"]*?)text-gray-500([^"]*?)"/g, to: 'className="$1$2" style={{ color: theme.textSecondary }}' },
  
  // Border replacements  
  { from: /className="([^"]*?)border-gray-200([^"]*?)"/g, to: 'className="$1$2" style={{ borderColor: theme.border }}' },
];

console.log('Applying theme fixes...');

files.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Add theme import if not present
    if (!content.includes("useTheme")) {
      content = content.replace(
        /import.*from.*ThemeContext.*;\n/,
        'import { useTheme } from \'../../../src/contexts/ThemeContext\';\n'
      );
      
      // Add theme hook
      content = content.replace(
        /export default function \w+\(\) \{\n/,
        match => match + '  const { theme, isDark } = useTheme();\n'
      );
    }
    
    // Apply replacements
    replacements.forEach(({ from, to }) => {
      content = content.replace(from, to);
    });
    
    fs.writeFileSync(filePath, content);
    console.log(`Fixed ${file}`);
  }
});

console.log('Theme fixes complete!');