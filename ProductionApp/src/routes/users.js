const express = require('express');
const User = require('../models/User');
const { protect, authorize } = require('../middleware/auth');
const { cacheMiddleware, invalidateCache } = require('../middleware/cache');
const router = express.Router();

// Apply protection to all routes
router.use(protect);

// @desc    Get all users
// @route   GET /api/users
// @access  Private/Admin
router.get('/', authorize('admin'), cacheMiddleware('short'), async (req, res, next) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;
    
    // Build filter
    const filter = {};
    if (req.query.role) filter.role = req.query.role;
    if (req.query.isActive !== undefined) filter.isActive = req.query.isActive === 'true';
    if (req.query.emailVerified !== undefined) filter.emailVerified = req.query.emailVerified === 'true';
    
    // Search
    if (req.query.search) {
      filter.$or = [
        { name: { $regex: req.query.search, $options: 'i' } },
        { email: { $regex: req.query.search, $options: 'i' } }
      ];
    }

    const total = await User.countDocuments(filter);
    const users = await User.find(filter)
      .select('-password -resetPasswordToken -resetPasswordExpire -emailVerificationToken')
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);

    res.status(200).json({
      success: true,
      data: {
        users,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      }
    });
  } catch (error) {
    next(error);
  }
});

// @desc    Get single user
// @route   GET /api/users/:id
// @access  Private/Admin or Own Profile
router.get('/:id', async (req, res, next) => {
  try {
    // Allow users to view their own profile or admins to view any profile
    if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
      return res.status(403).json({
        success: false,
        error: 'Not authorized to access this resource'
      });
    }

    const user = await User.findById(req.params.id)
      .select('-password -resetPasswordToken -resetPasswordExpire -emailVerificationToken');

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.status(200).json({
      success: true,
      data: { user }
    });
  } catch (error) {
    next(error);
  }
});

// @desc    Update user
// @route   PUT /api/users/:id
// @access  Private/Admin
router.put('/:id', authorize('admin'), invalidateCache(['short']), async (req, res, next) => {
  try {
    const { name, email, role, isActive, emailVerified } = req.body;
    
    const fieldsToUpdate = {};
    if (name !== undefined) fieldsToUpdate.name = name.trim();
    if (email !== undefined) fieldsToUpdate.email = email.toLowerCase().trim();
    if (role !== undefined) fieldsToUpdate.role = role;
    if (isActive !== undefined) fieldsToUpdate.isActive = isActive;
    if (emailVerified !== undefined) fieldsToUpdate.emailVerified = emailVerified;

    // Check if email is already taken by another user
    if (email) {
      const existingUser = await User.findOne({ 
        email: email.toLowerCase().trim(),
        _id: { $ne: req.params.id }
      });
      
      if (existingUser) {
        return res.status(400).json({
          success: false,
          error: 'Email already in use'
        });
      }
    }

    const user = await User.findByIdAndUpdate(
      req.params.id,
      fieldsToUpdate,
      {
        new: true,
        runValidators: true
      }
    ).select('-password -resetPasswordToken -resetPasswordExpire -emailVerificationToken');

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.status(200).json({
      success: true,
      message: 'User updated successfully',
      data: { user }
    });
  } catch (error) {
    next(error);
  }
});

// @desc    Delete user
// @route   DELETE /api/users/:id
// @access  Private/Admin
router.delete('/:id', authorize('admin'), invalidateCache(['short']), async (req, res, next) => {
  try {
    // Prevent admin from deleting themselves
    if (req.user.id === req.params.id) {
      return res.status(400).json({
        success: false,
        error: 'You cannot delete your own account'
      });
    }

    const user = await User.findByIdAndDelete(req.params.id);

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    res.status(200).json({
      success: true,
      message: 'User deleted successfully'
    });
  } catch (error) {
    next(error);
  }
});

// @desc    Unlock user account
// @route   PUT /api/users/:id/unlock
// @access  Private/Admin
router.put('/:id/unlock', authorize('admin'), invalidateCache(['short']), async (req, res, next) => {
  try {
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'User not found'
      });
    }

    // Reset login attempts and unlock account
    await user.resetLoginAttempts();

    res.status(200).json({
      success: true,
      message: 'User account unlocked successfully'
    });
  } catch (error) {
    next(error);
  }
});

// @desc    Get user statistics
// @route   GET /api/users/stats
// @access  Private/Admin
router.get('/stats/overview', authorize('admin'), cacheMiddleware('short'), async (req, res, next) => {
  try {
    // Use MongoDB aggregation with server-side date comparison
    const stats = await User.aggregate([
      {
        $facet: {
          // Calculate user counts using conditional sums
          counts: [
            {
              $group: {
                _id: null,
                total: { $sum: 1 },
                active: { $sum: { $cond: [{ $eq: ['$isActive', true] }, 1, 0] } },
                verified: { $sum: { $cond: [{ $eq: ['$emailVerified', true] }, 1, 0] } },
                // Use $$NOW for server-side date comparison
                locked: { $sum: { $cond: [{ $gt: ['$lockUntil', $$NOW] }, 1, 0] } }
              }
            }
          ],
          // Group by role
          byRole: [
            { $group: { _id: '$role', count: { $sum: 1 } } }
          ],
          // Get recent users
          recentUsers: [
            { $sort: { createdAt: -1 } },
            { $limit: 5 },
            { $project: { name: 1, email: 1, role: 1, isActive: 1, createdAt: 1 } }
          ]
        }
      }
    ]);

    // Extract and format the results
    const counts = stats[0].counts[0] || { total: 0, active: 0, verified: 0, locked: 0 };
    const usersByRole = stats[0].byRole.reduce((acc, curr) => {
      acc[curr._id] = curr.count;
      return acc;
    }, {});
    const recentUsers = stats[0].recentUsers;

    res.status(200).json({
      success: true,
      data: {
        statistics: {
          total: counts.total,
          active: counts.active,
          verified: counts.verified,
          locked: counts.locked,
          byRole: usersByRole
        },
        recentUsers
      }
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;