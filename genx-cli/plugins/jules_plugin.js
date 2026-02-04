function run(config) {
  console.log('Running Jules Plugin...');
  // In the future, this plugin could be used to:
  // - Scan code for issues
  // - Refactor code
  // - Run other plugins
  console.log('Jules Plugin finished.');
}

export default {
  description: 'A plugin for Jules to perform core development tasks.',
  run
};
